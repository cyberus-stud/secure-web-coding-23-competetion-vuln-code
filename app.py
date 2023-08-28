from flask import Flask, render_template, request, flash, url_for, redirect, session, Markup, render_template_string
from werkzeug.security import generate_password_hash
from datetime import timedelta, datetime
from database import *

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=5)
#########################################################
# WEEK HASHING
#########################################################
app.config['SECRET_KEY'] = 'SUPER_SECRET_KEY'
connection = create_sqlite_connection()

@app.route('/')
def home():
    if "username" in session:  # check if user's session is stored or not
        username = session["username"]  # getting username by his session
        
        return render_template('home.html', jobs=get_jobs_from_db(), username=username)
    else:
        flash("You are not logged in", category='success')
        return redirect(url_for("login"))

#########################################################
# PASSWORD POLICY & WEEK HASHING 
#########################################################
@app.route('/sign-up',  methods=['GET', 'POST'])
def sign_up():
    if request.method == 'GET':
        return render_template('sign_up.html')
    elif request.method == 'POST':
        # List of all required form fields
        required_fields = ['firstname', 'lastname', 'email', 'username', 'password1', 'password2', 'country', 'city',  'phone', 'birthdate']
        # Check if all fields are filled
        if all(request.form.get(field) for field in required_fields):
            # check if the user choosed valid email and user name that not already exist in the datbase
            if is_user_exist_in_db(email=request.form.get('email')):
                # the email already exists 
                flash('The email you have entered already exists, choose different one', category='error')
                return render_template('sign_up.html')
            
            if is_user_exist_in_db(username=request.form.get('username')):
                # the username already exists 
                flash('The username you have entered already exists, choose different one', category='error')
                return render_template('sign_up.html')

            #chek if the password and the confirm password are the same
            if request.form.get('password1') != request.form.get('password2'):
                 flash('The passwords should match each others', category='error')
                 return render_template('sign_up.html')

            # Process form data and save to the database
            data = {
                'firstname': request.form.get('firstname'),
                'lastname': request.form.get('lastname'),
                'email': request.form.get('email'),
                'username': request.form.get('username'),
                'password': generate_password_hash(request.form.get('password1'), method='md5'),
                'country': request.form.get('country'),
                'city': request.form.get('city'),
                'phone': request.form.get('phone'),
                'birthdate': datetime.strptime(request.form.get('birthdate'), '%Y-%m-%d')
            } 
            
            print(data['birthdate'])
            print(type(data['birthdate']))

            if add_user_to_db(data) != -1:
                # Store success message in the session
                flash('Congratulations! your account has been created successfully', category='success')
                return redirect(url_for('login'))
            else:
                flash('There was an error accured while creating your account', category='error')
                return redirect(url_for('home.html'))

#########################################################
# BRUTE-FORCING
#########################################################
@app.route('/login',  methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
      return  render_template('login.html')
    elif request.method == 'POST':    
         # List of all required form fields
        required_fields = ['username', 'password']
        if all(request.form.get(field) for field in required_fields):
            # user authentication 
            if check_password(username=request.form.get('username'), password=request.form.get('password')):
                # setting the session
                session.permanent = True
                username = request.form.get("username")  # get username from the form
                # set session of the user with username 
                session["username"] = username
                # setting the user id in the session 
                session["user_id"] = str(get_user_data_from_db(username=username)['id'])
                flash('Logged In Successfully', category='success')
                
                return redirect(url_for('home'))
            else:
                flash('The password or username you entered is not correct', category='error')
                return render_template('login.html')

#########################################################
# IDOR | WEEK HASHING & Cookie Tampering
#########################################################
@app.route('/admin/add-new-job', methods=['GET', 'POST'])
def add_new_job():
    if request.method == 'POST':
        data = {
            'title':request.form.get('title'),
            'location':request.form.get('location'),
            'salary':request.form.get('salary'),
            'currency':request.form.get('currency'),
            'responsibilities':request.form.get('responsibilities'),
            'requirements':request.form.get('requirements')
        }
        if add_job_to_db(data) != -1:
            flash('The new job has been added successfully', category='success')     
        else:
            flash('There was an error while adding the new job', category='error')       
        return redirect(url_for('home'))
    elif request.method == 'GET':
        if 'username' in session:
            logged_in_user = session['username']
            if logged_in_user == 'admin':
                return render_template('add_job.html')
            else:
                flash('YOU ARE NOT THE ADMIN, YOU DO NOT HAVE PERMISSION TO ACCESS THIS CONTENT !!', category='error')       
                return redirect(url_for('home'))

#########################################################
# SSTI
#########################################################               
@app.route('/job/<jid>')
def show_job_details(jid):
    job = get_job_from_db(jid)
    if not job :
        return "<h1>Not Found</h1>" , 404
    # Create a dictionary to map placeholders to actual values
    replacement_dict = {
		"$title$": job['title'],
		"$responsibilities$": job['responsibilities'],
		"$location$":job['location'],
		"$salary$": str(job['salary']),
		"$currency$": job['currency'],
	}
    with open('templates/job_details.html') as file:
        template_content = file.read()
		# Replace placeholders in the template content using the dictionary
        for placeholder, value in replacement_dict.items():
            template_content = template_content.replace(placeholder, value)
		# Render the template with replaced values and comments
        return render_template_string(template_content, job=job)

#########################################################
# Unrestricted File Uploading
#########################################################
@app.route('/job/<jid>/apply', methods=['GET', 'POST'])
def show_application_form(jid):
    job = get_job_from_db(jid)
    if not job:
        return "<h1>Not Found</h1>", 404
    
    if request.method == 'GET':
        return render_template('application_form.html', job=job)
    elif request.method == 'POST':
            # Process form data and save to the database
            cv_file = request.files['cv']
            cv_url = f"static/uploads/{cv_file.filename}"
            data = {
                'full_name': request.form.get('firstname') + ' ' + request.form.get('lastname'),
                'email': request.form.get('email'),
                'phone': request.form.get('phone'),
                'city': request.form.get('city'),
                'address': request.form.get('address'),
                'edu_experience': request.form.get('edu_experience'),
                'work_experience': request.form.get('work_experience'),
                'linkedin_url': request.form.get('linkedin_url'),
                'cv': cv_url
            }
            cv_file.save(cv_url)           
            if store_application_to_db(jid=jid,uid=session["user_id"], data=data) != -1:
                # Store success message in the session
                flash('Congratulations! your application has been submitted successfully', category='success')
                return redirect(url_for('home'))
            else:
                flash('There was an error accured while submitting your application', category='error')
                return render_template('application_form.html', job=job)

#########################################################
# SQL INGECTION
#########################################################
@app.route('/search')
def search_job():
    job_name = request.args.get('job_name')
    jobs = job_search(job_name=job_name)
    return render_template('search_result.html', jobs=jobs, job_name=job_name)

@app.route('/courses', methods=['GET', 'POST'])
def show_courses():
    return render_template('courses.html', courses=get_courses_from_db())

#########################################################
# PIRCE MANIPULATION
#########################################################
@app.route('/courses/<cid>/enroll', methods=['GET', 'POST'])
def enroll_course(cid):
    course = get_course_from_db(cid)
    if request.method == 'GET':
        return render_template('enroll_course.html', course=course)
    elif request.method == 'POST':
        form_data = request.form
        price = form_data.get('price')
        currency = form_data.get('currency')
        enroll_course_in_db( course_id=cid, user_id=session['user_id'])
        flash(f'Congratulations !! you have got the course with {price} {currency}', category='success')
        return redirect(url_for('show_courses'))

#########################################################
# XSS
#########################################################
@app.route('/courses/<cid>/content', methods=['GET', 'POST'])
def show_course_content(cid):
    course = get_course_from_db(cid)
    course_reviews=get_course_reviews_from_db(cid)
    reviews = [Markup(review) for review in course_reviews]
    if request.method == 'GET':
        if is_enrolled_in_course(user_id=session['user_id'], course_id=cid):
            return render_template('course_content.html', course=course, user_id=session['user_id'], reviews=reviews)
        else:
            flash("Sorry you are not enrolled in this course, you have to enroll first to access this content", category='error')
            return redirect(url_for('show_courses'))
    elif request.method == 'POST':
        review =  Markup(request.form.get('review'))  
        data={
            'course_id':cid,
            'user_id': session['user_id'],
            'review': review.strip()
        }
        add_course_review_to_db(data)
        flash("Your has been added successfully!", category='success')      
        return render_template('course_content.html', course=course, review=review, reviews=reviews)

if __name__ == '__main__': 
    init_db(connection)
    app.run(debug=True)
    
