from io import BytesIO
import logging
import plotly.graph_objects as go
import pandas as pd
from VideoGen.info import TableInfo, ImageInfo
from VideoGen.infra import LoggerFactory
from VideoGen.storage import BaseStorage

class TableVisualizer:
    def __init__(
            self, 
            storage:BaseStorage, 
            logger: logging.Logger = None
    ):
        self.storage: BaseStorage = storage
        self.logger: logging.Logger = logger or LoggerFactory.get_logger(TableVisualizer.__name__)


    def draw_table(self, table: TableInfo) -> ImageInfo:
        df = pd.DataFrame(table.path)
        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(values=list(df.columns),align='center'),
                    cells=dict(
                        values=df.values.transpose(),
                        fill_color = [["white","lightgrey"]*df.shape[0]],
                        align='center'
                    )
                )
            ]
        )
        image_data = BytesIO()
        fig.write_image(image_data,scale=6)
        id, save_path = self.storage.save_image_content(image_data, 'png')
        image_info = ImageInfo(id=id, path=save_path, name=table.name)
        self.storage.save_image_metadata(image_info, id)
        
        return image_info