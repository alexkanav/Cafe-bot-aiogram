import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials


class GoogleSheets:
    menu = []

    def __init__(self, key_file: str):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            key_file, ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        )
        http_auth = credentials.authorize(httplib2.Http())
        self.service = apiclient.discovery.build('sheets', 'v4', http=http_auth)

    def receive_from_google_sheet(self, sheets_id: str, cell_range: str, dimension: str = 'ROWS') -> list[list[str]]:
        read_values: dict = self.service.spreadsheets().values().get(
            spreadsheetId=sheets_id,
            range=cell_range,
            majorDimension=dimension
        ).execute()
        values = read_values.get('values')
        GoogleSheets.menu.append(values)
        return values

    def change_google_sheet(self, values: list[list[str]], sheets_id: str, cell_range: str, dimension: str = 'ROWS'):
        write_values = self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=sheets_id,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {"range": cell_range,
                     "majorDimension": dimension,
                     "values": values}
                ]
            }
        ).execute()
