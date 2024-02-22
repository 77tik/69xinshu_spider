from projectA.tests.db import DbUtils


class Task(object):

    def __init__(self,name,url,status):

        self.name = name
        self.url = url
        self.status = status
    def save(self):
        db = DbUtils(host='localhost',username='root',password='xq200431',port=3306,db='novels')
        sql = f"insert into tasks values('{self.name}','{self.url}','{self.status}')"
        db.insert(sql)


if __name__ == '__main__':
    url = 'www.baidu.com'
    task_test = Task(name=f"抓取{url}",url=url,status='doing')
    task_test.save()
