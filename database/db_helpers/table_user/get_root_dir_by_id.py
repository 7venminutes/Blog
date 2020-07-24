import pymysql

from const_var import FileCube_DbConfig


def get_root_dir_by_id(user_id):
    """
    根据用户ID获取用户的根目录
    :param user_id: 不超过二十位的字符串
    :return: state: ..., root_dir: ..., details: ...
    """
    state = False
    details = ''
    root_dir = ''
    user_id = str(user_id)
    if len(user_id) > 20:
        details = 'user_id的长度不应该大于20，数据库中存储类型为VARCHAR(20)'
        return state, root_dir, details
    conn = pymysql.connect(host=FileCube_DbConfig['host'], port=FileCube_DbConfig['port'], user=FileCube_DbConfig['user'],
                           passwd=FileCube_DbConfig['pwd'], db=FileCube_DbConfig['db_name'], charset='utf8')
    cursor = conn.cursor()
    count = cursor.execute("SELECT root_dir FROM USER WHERE ID='" + user_id + "';")
    if count == 0:
        details = user_id + '无对应的root_dir'
    else:
        state = True
        result = cursor.fetchall()
        for row in result:
            root_dir = row[0]
        if count > 1:
            details = '查询到不止一条根目录，请检查其他流程，已返回最后一条数据'
        else:
            details = '返回根目录成功'
    conn.close()
    return state, root_dir, details
