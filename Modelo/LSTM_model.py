# Librerias

import numpy
import pandas as pd
import math
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import psycopg2 # libreria que permite la coneccion con la base de datos
import time
import numpy as np
import pickle
from datetime import timedelta
import os

# Parametros que se consideraran en el modelo
#%%

look_back = 7 # Dias que se necesitan para hacer el pronostico
units = 1 # Inudades de LSTM
cut_off_day = 7 # Dia de corte para comenzar hacer la prediccion
epoc = 1000 # Numero de epocas para la red
val_spit = 0.1 # Porsentaje de validacion

# Coneccion a la base de datos y extraccion de la informacion
#%%


conn = psycopg2.connect(host="umovilgr81.cwwzdzhdizxh.us-east-2.rds.amazonaws.com",
                        port = 5432, database="transporte", 
                        user="postgres", password="qUIup2lwFxoXh9yEXo4P")

query = """SELECT terminal ,fecha_despacho, SUM(pasajeros) AS pasajeros FROM pasajeros_origen_destino_ultima3
            WHERE fecha_despacho BETWEEN '2020-10-01' AND '2021-08-15'
            GROUP BY terminal, fecha_despacho;
        """

cur = conn.cursor()
cur.execute(query)
query_results = cur.fetchall()
cur.close()

dataset = pd.DataFrame(query_results,columns = ['terminal','fecha','pasajeros'])

del query, conn, query_results


# Dias festivos
festivos=['2020-10-11',
        '2020-11-01',
        '2020-11-15',
        '2020-12-09',
        '2020-12-24',
        '2020-12-31',
        '2021-01-10',
        '2021-03-21',
        '2021-03-31',
        '2021-04-30',
        '2021-05-16',
        '2021-06-06',
        '2021-06-13',
        '2021-07-04',
        '2021-07-19',
        '2021-08-06',
        '2021-08-15']

fesivos_restantes2021=['2021-10-17',
                       '2021-10-31',
                       '2021-11-14',
                       '2021-12-07',
                       '2021-12-24']
fesivos_restantes2021 = pd.to_datetime(fesivos_restantes2021)




dataset["fecha"]=pd.to_datetime(dataset["fecha"])

inicio= pd.to_datetime('2021-04-27')
fin= pd.to_datetime('2021-06-21')
dataset = dataset[(dataset['fecha']<inicio) | (dataset['fecha']>fin) ]


festivos = pd.to_datetime(festivos)
dataset["festivo"]= [1  if x in festivos else 0 for x in dataset['fecha']]
dataset['fds']=np.where((dataset['fecha'].dt.dayofweek) < 5,0,1)

fechas = dataset[['fecha','festivo','fds']].drop_duplicates()


df = dataset.copy()


# Preparacion de los datos
#%%

dict_modelos = {}

for terminal in df['terminal'].unique():

    dataset = df[df['terminal'] == terminal]   
    dataset.drop(columns=['terminal'],axis=1,inplace = True)
    dataset = dataset.merge(fechas,on=['fecha','festivo','fds'],how = 'right')
    dataset = dataset.sort_values(by = 'fecha')
    
    dataset['pasajeros'] = dataset['pasajeros'].interpolate(axis=0)
    dataset['pasajeros'] = dataset['pasajeros'].fillna(method = 'backfill',axis=0)
    
    dataset = dataset.reset_index(drop = True)
         

    # Datos de entranamiento y de test
    dataset_train = dataset[:-cut_off_day]
    dataset_train = pd.DataFrame(dataset_train).reset_index(drop= True)
    
    dataset_test = dataset[-(cut_off_day+look_back):]
    dataset_test = pd.DataFrame(dataset_test).reset_index(drop= True)
      
    
    # Normalizacion de los datos 
    scaler = MinMaxScaler(feature_range=(0, 1))
    
    values = dataset_train['pasajeros'].values.reshape(-1,1)
    dataset_train['norm_pasajeros'] = scaler.fit_transform(values)
    
    values = dataset_test['pasajeros'].values.reshape(-1,1)
    dataset_test['norm_pasajeros'] = scaler.transform(values)
    
    
    # Se organiza los datos  de entrenamiento con las dimensiones adecuadas
    trainX = dataset_train['norm_pasajeros'].values[:-1]
    trainX_festivo = dataset_train['festivo'].values[:-1]
    trainX_fds = dataset_train['fds'].values[:-1]
    trainX_vec = []
    for i in range(len(trainX)-look_back+1):
        trainX_vec.append([trainX[i:i+look_back],trainX_festivo[i:i+look_back],trainX_fds[i:i+look_back]])
    
    trainX_vec = np.array(trainX_vec)
    trainX_vec = trainX_vec.reshape(trainX_vec.shape[0],3,look_back)
        
    trainY = dataset_train['norm_pasajeros'].values[look_back:]
      
    
    # Se organiza los datos  de prueba con las dimensiones adecuadas
    testX = dataset_test['norm_pasajeros'].values[:-1]
    testX_festivo = dataset_train['festivo'].values[:-1]
    testX_fds = dataset_train['fds'].values[:-1]
    testX_vec = []
    for i in range(len(testX)-look_back+1):
        testX_vec.append([testX[i:i+look_back],testX_festivo[i:i+look_back],testX_fds[i:i+look_back]])
    
    testX_vec = np.array(testX_vec)
    testX_vec = testX_vec.reshape(testX_vec.shape[0],3,look_back)
    
    testY = dataset_test['norm_pasajeros'].values[look_back:]
    
    
    # Modelo LSTM con los parametros asignados
    #%%
    
    numpy.random.seed(15489635)
    
    
    model = Sequential()
    model.add(LSTM(units, input_shape=(3, look_back))) # Se incorporta la capa LSTM
    model.add(Dense(1)) # Se requeire cuando hay varias unidades
    model.compile(loss='mean_squared_error', optimizer='adam')
    
     
    # Se ajusta el modelo con los datos de entrenamiento
    
    start = time.time() 
    hist = model.fit(trainX_vec, trainY, epochs=epoc, batch_size=5, verbose=2,validation_split=val_spit)
    end = time.time() 
    time_training = (end-start)/60

    # print('Trining time: {:.2f} min'.format(time_training))
    
    # Generacion de las predicciones 
    #%%
    
    # Se hace la prediccion para los datos de entrenamiento
    trainPredict = model.predict(trainX_vec)
    
    # Invierte el escalamieto de los datos de entrenamiento
    trainPredict = scaler.inverse_transform(trainPredict)
    trainY = scaler.inverse_transform([trainY])
    
    # Se calcula la raiz del error cuadratico medio
    trainScore = math.sqrt(mean_squared_error(trainY[0], trainPredict[:,0]))
    trainScore_Relative = math.sqrt(mean_squared_error(trainY[0], trainPredict[:,0]))/np.mean(trainY[0])
    # print('Train Score: %.2f RMSE' % (trainScore))
    # print('Train Score Relative: %.2f RMSE' % (trainScore_Relative))
    
    
    # Se aplica el mismo proceso anterior pero con los datos de prueba
    testPredict = model.predict(testX_vec)
    testPredict = scaler.inverse_transform(testPredict)
    testY = scaler.inverse_transform([testY])
    testScore = math.sqrt(mean_squared_error(testY[0], testPredict[:,0]))
    testScore_Relative = math.sqrt(mean_squared_error(testY[0], testPredict[:,0]))/np.mean(testY[0])
    # print('Test Score: %.2f RMSE' % (testScore))
    # print('Test Score Relative: %.2f RMSE' % (testScore_Relative))
    

    # Se crea la serie de tiempo de las predicciones
    trainPredictPlot = dataset_train[look_back:].copy()
    trainPredictPlot['predict_pasajeros'] = trainPredict
    
    # Se crea la serie de tiempo de las pruebas
    testPredictPlot = dataset_test[look_back:].copy()
    testPredictPlot['predict_pasajeros'] = testPredict



    # Forecasting hasta el 15 de septiembre 
    
    forecasting_start = dataset[-cut_off_day:]
        
    forecasting_start.reset_index(drop=True,inplace = True)
        
    values = forecasting_start['pasajeros'].values.reshape(-1,1)
        
    forecasting_start['norm_pasajeros'] = scaler.transform(values)
    
    

    for i in range(32):
        
        
        n = len(forecasting_start)
        
        forecasting_vec = forecasting_start[-cut_off_day:]
                    
        X = forecasting_vec['norm_pasajeros'].values
        X_festivo = forecasting_vec['festivo'].values
        X_fds = forecasting_vec['fds'].values
        
        X_vec = np.array([[X,X_festivo,X_fds]])
                
        forecasting = model.predict(X_vec)
        forecasting = scaler.inverse_transform(forecasting)
        nor_forecasting = scaler.transform(forecasting)[0][0]       
        nex_day = forecasting_vec['fecha'][n-1]+timedelta(days=1)      
        fds = nex_day.dayofweek > 4
        fes = nex_day in fesivos_restantes2021
               
        forecasting_start = forecasting_start.append({'fecha':nex_day,'pasajeros':int(forecasting[0][0]),
                                'festivo':fes,'fds':fds,'norm_pasajeros':nor_forecasting},
                               ignore_index = True)
    

    
    # Guardar resultados 
    
    dict_modelos[terminal] = {'scaler':scaler,'model':model,'time':time_training,
    'metrics':{"Test Score":testScore,"Test Score Relative":testScore_Relative,
    'Train Score':trainScore,'Train Score Relative':trainScore_Relative},
    'datasets':{'trainPredictPlot':trainPredictPlot,'testPredictPlot':testPredictPlot,'dataset':dataset,
                'forecasting':forecasting_start}}




for terminal in dict_modelos:
    
    # Guardar el Modelo
    model = dict_modelos[terminal]['model']
    model.save(os.path.join(f'pages/Predicciones/Datos/Modelos terminales/{terminal} modelos.h5'))
            
    del dict_modelos[terminal]['model']
    

with open(os.path.join('pages/Predicciones/Datos/Modelos terminales/dict_modelos.pkl'),'wb') as f:
    pickle.dump(dict_modelos,f)










