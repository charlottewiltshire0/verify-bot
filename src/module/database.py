# import psycopg2
# from psycopg2 import Error
#
#
# class PostgreSQLDB:
#     def __init__(self, dbname, user, password, host='localhost', port='5432'):
#         self.dbname = dbname
#         self.user = user
#         self.password = password
#         self.host = host
#         self.port = port
#         self.connection = None
#         self.cursor = None
#
#     def connect(self):
#         try:
#             self.connection = psycopg2.connect(
#                 dbname=self.dbname,
#                 user=self.user,
#                 password=self.password,
#                 host=self.host,
#                 port=self.port
#             )
#             self.cursor = self.connection.cursor()
#             print("Connected to PostgreSQL")
#         except Error as e:
#             print(f"Error connecting to PostgreSQL: {e}")
#
#     def disconnect(self):
#         if self.connection:
#             self.cursor.close()
#             self.connection.close()
#             print("PostgreSQL connection is closed")
#
#     def execute_query(self, query):
#         try:
#             self.cursor.execute(query)
#             self.connection.commit()
#             print("Query executed successfully")
#         except Error as e:
#             print(f"Error executing query: {e}")
#
#     def fetch_data(self, query):
#         try:
#             self.cursor.execute(query)
#             rows = self.cursor.fetchall()
#             return rows
#         except Error as e:
#             print(f"Error fetching data: {e}")
#             return None