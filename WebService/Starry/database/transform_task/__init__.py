import logging
import pymysql
import time

from const_var import Starry_DbConfig

TRANSFORM_TASK = 'transform_task_' + time.strftime("%Y%m%d")

logging.basicConfig(level=logging.NOTSET)


def create_table_transform_task():
    conn = pymysql.connect(host=Starry_DbConfig['host'],
                           port=Starry_DbConfig['port'],
                           user=Starry_DbConfig['user'],
                           passwd=Starry_DbConfig['pwd'],
                           db=Starry_DbConfig['db_name'],
                           charset='utf8')
    cursor = conn.cursor()
    date_string = time.strftime("%Y%m%d")
    count = cursor.execute("SHOW TABLES LIKE '%s'" % ('transform_task_' + date_string))
    if count == 0:
        cursor.execute('''
            CREATE TABLE %s
            (
                task_id VARCHAR(128) NOT NULL,
                task_status ENUM('new', 'processing', 'success', 'failed') NOT NULL,
                user_id VARCHAR(20) NOT NULL,
                ipv4_ip VARCHAR(15),
                request_start_time DATETIME NOT NULL,
                task_finish_time DATETIME,
                original_image_path VARCHAR(128) NOT NULL,
                transformed_image_path VARCHAR(128),
                image_type ENUM('png', 'jpg') NOT NULL,
                selected_style VARCHAR(20) NOT NULL,
                
                PRIMARY KEY (task_id)
            );
        ''' % ('transform_task_' + date_string))
        conn.commit()
        logging.info('%s created successfully' % ('transform_task_' + date_string))
    else:
        logging.info('%s already existed in %s, skipped'
                     % ('transform_task_' + date_string,
                        Starry_DbConfig['db_name']))
    conn.close()


create_table_transform_task()
