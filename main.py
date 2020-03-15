import mysql.connector
import pandas as pandas
import matplotlib.pyplot as plot
import math
import json
import os


# Query will be read from the filename provided.
class MySQLPlotter:
    context = None
    cursor = None
    query = None
    config = None
    query_file = None
    graph_colors = ['pink', 'blue', 'yellow', 'green']

    def __init__(self, filename):
        self._load_config()
        self._init_connection()
        self.query_file = filename
        self._read_query("queries\\" + filename)

    # Aggregate all headers before value_column, and plot the rest columns as line chart.
    # @Param value_column: indicate last x columns are for y-axis
    def query_and_plot(self, value_column):
        self.cursor.execute(self.query)
        dimensions = list(map(lambda desc: desc[0], self.cursor.description))
        data = {
            'headers': [],
        }
        for item in [list(elem) for elem in self.cursor]:
            aggregated_headers = ""
            for i in range(0, len(dimensions)):
                if i < len(dimensions) - value_column:
                    aggregated_headers += " " + item[i].strip()
                else:
                    dimension = dimensions[i]
                    if dimension not in data:
                        data[dimension] = []
                    data[dimension].append(math.floor(item[i]))
            data['headers'].append(aggregated_headers)
        self._plot(data, 'headers', dimensions[-value_column:])

    def close(self):
        self.cursor.close()
        self.context.close()
        self.cursor = None
        self.context = None

    def _load_config(self):
        f = open('config', 'r')
        self.config = json.loads(f.read())
        if not os.path.isdir(self.config['output_dir']):
            os.mkdir(self.config['output_dir'])

    def _read_query(self, filename):
        f = open(filename, 'r')
        self.query = f.read()

    def _init_connection(self):
        try:
            self.context = mysql.connector.connect(**self.config['db_config'])
            self.cursor = self.context.cursor()
        except mysql.connector.Error as err:
            print(err)

    def _plot(self, data, x_axis, list_y_axis):
        df = pandas.DataFrame(data)
        print(df)
        ax = plot.gca()
        for i in range(0, len(list_y_axis)):
            df.plot(kind='line', x=x_axis, y=list_y_axis[i], color=self.graph_colors[i], ax=ax)
        plot.gcf().subplots_adjust(bottom=0.3)
        plot.xticks(rotation="vertical")
        plot.savefig(self._build_output_file())
        plot.clf()

    def _build_output_file(self):
        return self.config['output_dir'] + '\\' + self.query_file + '.png'


for f in os.listdir('queries'):
    number_of_y_axis = int(f.split('.')[0].split('_')[-1])

    MySQLPlotter(f).query_and_plot(number_of_y_axis)

