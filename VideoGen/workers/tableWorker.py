import os
import plotly.graph_objects as go
import pandas as pd
from VideoGen.info import TableInfo

class TableWorker:
    @staticmethod
    def draw_table(table: TableInfo, output_dir:str, file_suffix:str):
        df = pd.DataFrame(table.content)
        path = os.path.join(output_dir, "go_table_{}.png".format(file_suffix))

        fig = go.Figure(data=[
                            go.Table(
                            header=dict(values=list(df.columns),align='center'),
                            cells=dict(values=df.values.transpose(),
                                        fill_color = [["white","lightgrey"]*df.shape[0]],
                                        align='center'
                                        )
                                )
                            ])
        fig.write_image(path,scale=6)
        return path