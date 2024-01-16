"""main file of project, this file run dash app
"""


from app import app

from routes import render_page_content
from pages.analysis.routes.routes_analysis import update_graph
from pages.analysis.terminals.terminals_analysis import fig_heatmap




if __name__ == "__main__":
    app.run_server(debug=True)
    # app.run_server(host='0.0.0.0', port=8050,debug=False) 