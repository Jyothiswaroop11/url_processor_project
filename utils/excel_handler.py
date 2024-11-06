import openpyxl
import allure

class ExcelHandler:
    @staticmethod
    @allure.step("Loading Excel workbook")
    def load_workbook(file_path):
        """Load Excel workbook"""
        try:
            return openpyxl.load_workbook(file_path)
        except Exception as e:
            allure.attach(
                body=f"Error loading Excel file: {str(e)}",
                name="Excel Error",
                attachment_type=allure.attachment_type.TEXT
            )
            raise

    @staticmethod
    def get_sheet(workbook, sheet_name):
        """Get sheet from workbook"""
        if sheet_name not in workbook.sheetnames:
            raise ValueError(f"Sheet '{sheet_name}' not found in workbook")
        return workbook[sheet_name]

    @staticmethod
    def get_row_count(file, sheet_name):
        """Get total number of rows in sheet"""
        workbook = ExcelHandler.load_workbook(file)
        sheet = ExcelHandler.get_sheet(workbook, sheet_name)
        return sheet.max_row

    @staticmethod
    @allure.step("Reading Excel data")
    def read_data(file, sheet_name, rownum, columnno):
        """Read data from specific cell"""
        workbook = ExcelHandler.load_workbook(file)
        sheet = ExcelHandler.get_sheet(workbook, sheet_name)
        return sheet.cell(row=rownum, column=columnno).value

    @staticmethod
    @allure.step("Writing Excel data")
    def write_data(file, sheet_name, rownum, columnno, data):
        """Write data to specific cell"""
        workbook = ExcelHandler.load_workbook(file)
        sheet = ExcelHandler.get_sheet(workbook, sheet_name)
        sheet.cell(row=rownum, column=columnno).value = data
        workbook.save(file)