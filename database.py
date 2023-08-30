import sqlite3
from werkzeug.security import check_password_hash

# Function to create SQLite3 connection
def create_sqlite_connection(name='database.db'):
    return sqlite3.connect(name, check_same_thread=False)

# Initialize SQLite3 database
def init_db(connection):
    cursor = connection.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            email TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            country TEXT NOT NULL,
            city TEXT NOT NULL,
            phone TEXT NOT NULL,
            birthdate DATE NOT NULL
        )
    ''')

    # Create jobs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            location TEXT NOT NULL,
            salary INTEGER DEFAULT NULL,
            currency TEXT DEFAULT NULL,
            responsibilities TEXT DEFAULT NULL,
            requirements TEXT DEFAULT NULL
        )
    ''')

    # Create applications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            city TEXT NOT NULL,
            address TEXT NOT NULL,
            edu_experience TEXT NOT NULL,
            work_experience TEXT NOT NULL,
            linkedin_url TEXT NOT NULL,
            cv TEXT NOT NULL,
            job_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (job_id) REFERENCES jobs(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Create courses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price INTEGER NOT NULL,
            currency TEXT NOT NULL
        )
    ''')

    # Create enrolled_courses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS enrolled_courses (
            course_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (course_id) REFERENCES courses(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Create course_reviews table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS course_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            review TEXT NOT NULL,
            FOREIGN KEY (course_id) REFERENCES courses(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    connection.commit()

def get_jobs_from_db():
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()
        result = cursor.execute('SELECT * FROM jobs')
        
        jobs_dicts = []
        columns = [column[0] for column in result.description]  # Retrieve column names
        
        for row in result.fetchall():
            row_dict = dict(zip(columns, row))
            jobs_dicts.append(row_dict)
            
    return jobs_dicts

def get_job_from_db(jid):
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()
        result = cursor.execute("SELECT * FROM jobs WHERE id = ?", (jid,))
        row = result.fetchone()
        if row:
            columns = [column[0] for column in result.description]
            job_dict = dict(zip(columns, row))
            return job_dict
        else:
            return None

def store_application_to_db(jid, uid, data):
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()
        query = '''
            INSERT INTO applications(full_name, email, phone, city, address, edu_experience, work_experience, linkedin_url, cv, job_id, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        try:
            data['jid'] = jid
            data['user_id'] = uid
            cursor.execute(query, (
                data['full_name'],
                data['email'],
                data['phone'],
                data['city'],
                data['address'],
                data['edu_experience'],
                data['work_experience'],
                data['linkedin_url'],
                data['cv'],
                data['jid'],
                data['user_id']
            ))
            conn.commit()
        except Exception as e:
            return -1

def add_job_to_db(data):
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()
        query = '''
            INSERT INTO jobs(title, location, salary, currency, responsibilities, requirements)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        try:
            cursor.execute(query, (
                data['title'],
                data['location'],
                data['salary'],
                data['currency'],
                data['responsibilities'],
                data['requirements']
            ))
            conn.commit()
        except Exception as e:
            return -1

def job_search(job_name):
    with create_sqlite_connection() as conn:
        query = f"SELECT * FROM jobs WHERE title = '{job_name}'"
        try:
            result = conn.execute(query)
            jobs_dicts = []
            for row in result.fetchall():
                columns = [column[0] for column in result.description]
                job_dict = dict(zip(columns, row))
                jobs_dicts.append(job_dict)
            return jobs_dicts
        except Exception as e:
            return e

def add_user_to_db(data):
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()
        query = '''
            INSERT INTO users(firstname, lastname, email, username, password, country, city, phone, birthdate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        try:
            cursor.execute(query, (
                data['firstname'],
                data['lastname'],
                data['email'],
                data['username'],
                data['password'],
                data['country'],
                data['city'],
                data['phone'],
                data['birthdate']
            ))
            conn.commit()
        except Exception as e:
            return -1

def is_user_exist_in_db(email=None, username=None):
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()
        if email:
            query = 'SELECT * FROM users WHERE email = ?'
            params = (email,)
        elif username:
            query = 'SELECT * FROM users WHERE username = ?'
            params = (username,)
        else:
            return False  # Invalid parameters provided
        
        result = cursor.execute(query, params)
        rows = result.fetchall()
        return len(rows) > 0

def get_user_data_from_db(email=None, username=None):
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()
        if email:
            query = 'SELECT * FROM users WHERE email = ?'
            params = (email,)
        elif username:
            query = 'SELECT * FROM users WHERE username = ?'
            params = (username,)
        else:
            return None  # Invalid parameters provided
        
        result = cursor.execute(query, params)
        row = result.fetchone()
        if row:
            columns = [column[0] for column in result.description]
            user_dict = dict(zip(columns, row))
            return user_dict
        else:
            return None

def get_user_password_from_db(email=None, username=None):
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()
        if email:
            query = 'SELECT password FROM users WHERE email = ?'
            params = (email,)
        elif username:
            query = 'SELECT password FROM users WHERE username = ?'
            params = (username,)
        else:
            return None  # Invalid parameters provided
        
        result = cursor.execute(query, params)
        row = result.fetchone()
        if row:
            return row[0]
        else:
            return None

def check_password(username, password):
    correct_password_hash = get_user_password_from_db(username=username)
    try:
        if correct_password_hash and check_password_hash(correct_password_hash, password):
            return True
        else:
            return False
    except Exception as e:
        return False

def get_courses_from_db():
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()
        result = cursor.execute('SELECT * FROM courses')
        courses_dicts = []
        columns = [column[0] for column in result.description]  # Retrieve column names
        
        for row in result.fetchall():
            row_dict = dict(zip(columns, row))
            courses_dicts.append(row_dict)

    return courses_dicts

def get_course_from_db(cid):
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()
        result = cursor.execute("SELECT * FROM courses WHERE id = ?", (cid,))
        row = result.fetchone()
        if row:
            columns = [column[0] for column in result.description]
            course_dict = dict(zip(columns, row))
            return course_dict
        else:
            return None

def enroll_course_in_db(user_id, course_id):
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()
        query = 'INSERT INTO enrolled_courses(course_id, user_id) VALUES (?, ?)'
        try:
            cursor.execute(query, (course_id, user_id))
            conn.commit()
        except:
            return -1

def is_enrolled_in_course(user_id, course_id):
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()
        query = 'SELECT * FROM enrolled_courses WHERE user_id = ? AND course_id = ?'
        params = (user_id, course_id)
        result = cursor.execute(query, params)
        rows = result.fetchall()
        return len(rows) > 0

def add_course_review_to_db(data):
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()
        query = '''
            INSERT INTO course_reviews(course_id, user_id, review)
            VALUES (?, ?, ?)
        '''
        try:
            cursor.execute(query, (
                data['course_id'],
                data['user_id'],
                data['review']
            ))
            conn.commit()
        except Exception as e:
            return -1
        
def get_course_reviews_from_db(course_id):
    with create_sqlite_connection() as conn:
        cursor = conn.cursor()
        result = cursor.execute('SELECT review FROM course_reviews WHERE course_id = ?', (course_id,))
        reviews = []
        columns = [column[0] for column in result.description]  # Retrieve column names
        
        for row in result.fetchall():
            row_dict = dict(zip(columns, row))
            reviews.append(row_dict['review'])

    return reviews





