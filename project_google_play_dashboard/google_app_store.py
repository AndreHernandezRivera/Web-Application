from google_play_scraper import Sort, reviews_all, app
import pandas as pd
import psycopg2
from psycopg2 import extras

import authentication_info_for_database
AUTH=authentication_info_for_database.credentials()
file_dir_and_name='C:/Users/Andre/.spyder-py3/project_google_play_dashboard/google_reviews_ca_filterless.csv'
country_code='ca' #### countrycodes are a thing: https://stackoverflow.com/questions/11825318/how-to-explore-web-based-google-play-in-another-country

# i'm hardcoding the table name and you can't stop me :)


print('fetching data...')
result = reviews_all(
	'com.drop.loyalty.android',
	sleep_milliseconds=0, # defaults to 0
	lang='en', # defaults to 'en'
	country=country_code, # defaults to 'us'
	sort=Sort.MOST_RELEVANT, # defaults to Sort.MOST_RELEVANT
	filter_score_with=None # defaults to None(means all score)
)
print('got the data...')

def produce_sql_table_command(columnName,columnDataType):
	
	createTableStatement = 'CREATE TABLE IF NOT EXISTS canada_filterless ('
	for i in range(len(columnDataType)):
		createTableStatement = createTableStatement + '\n' + columnName[i] + ' ' + columnDataType[i] + ','
	createTableStatement = createTableStatement[:-1] + ' );'
	
	return createTableStatement
	
	
def getColumnDtypes(dataTypes):
	
	dataList = []
	for x in dataTypes:
		if(x == 'int64'):
			dataList.append('int')
		elif (x == 'float64'):
			dataList.append('float')
		elif (x == 'bool'):
			dataList.append('boolean')
		else:
			dataList.append('varchar')
	return dataList

def execute_sql_command(sql_command_string):
	connection = psycopg2.connect(user=AUTH[0],
								  password=AUTH[1],
								  database=AUTH[2])   
	cur = connection.cursor()
	cur.execute(sql_command_string)
	connection.commit()
	if(connection):
		connection.close()

def add_df_to_sql_table(df,table):
	### this will add data!
	connection = psycopg2.connect(user=AUTH[0],
								  password=AUTH[1],
								  database=AUTH[2]) 	
	if len(df) > 0:
		df_columns = list(df)
		# create (col1,col2,...)
		columns = ",".join(df_columns)

		# create VALUES('%s', '%s",...) one '%s' per column
		values = "VALUES({})".format(",".join(["%s" for i in df_columns])) 
		
		
		#create INSERT INTO table (columns) VALUES('%s',...)
		insert_stmt = "INSERT INTO {} ({}) {}".format(table,columns,values)
	

		df=df.astype(str) # any issues can be fixed manually using SQL:  https://stackoverflow.com/questions/26439033/change-column-datatype-from-text-to-integer-in-postgresql
		#https://www.postgresql.org/docs/current/functions-formatting.html

	cur = connection.cursor()
	psycopg2.extras.execute_batch(cur, insert_stmt, df.values)
	connection.commit()
	cur.close()
		
	if(connection):
		connection.close()

print(result[0])

df = pd.DataFrame(result)
columnName = list(df.columns.values)
columnDataType = getColumnDtypes(df.dtypes)

#### we make a table IF IT DOES NOT EXIST ALREADY, therefore run this command once, and delete the table if it already exists so it updates with your new command!
sql_make_table_command=produce_sql_table_command(columnName,columnDataType) # we generate the create table sql command here
sql_make_table_command_string=f'{sql_make_table_command}'
execute_sql_command(sql_make_table_command_string)


add_df_to_sql_table(df,'canada_filterless')

#### below could work if we put the output in the temp directory
#exporting_db_to_csv=f'COPY canada_filterless TO \'{file_dir_and_name}\' DELIMITER \',\' CSV HEADER;'
#execute_sql_command(exporting_db_to_csv)
df.to_csv(file_dir_and_name)

