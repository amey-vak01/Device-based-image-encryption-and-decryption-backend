from flask import Flask, redirect, send_file, url_for, render_template, request
from hashlib import md5
import os
import smtplib
from numpy import full
from random_object_id import generate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from flask_cors import CORS, cross_origin



smtp_email = 'aditya.kumar3006@gmail.com'
smtp_password ="iznhblozknvgsilu"



from Crypto.Cipher import DES3
full_path = os.path.realpath(__file__)

UPLOAD_FOLDER = os.path.dirname(full_path) + '\\images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__,template_folder='Templates', static_folder='images')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER




@app.route('/')
@cross_origin()
def welcome():
    return render_template('index.html')






### Result checker submit html page
@app.route('/submit', methods=['POST', 'GET'])
@cross_origin()
def submit(operation=None):
    total_score = 0
    if request.method == 'POST':
        print(request.form)
        choice = (request.form['choose'])
        key = (request.form['id'])
        
        if 'image_file' not in request.files:
            return "File not found"
            
        target = request.files['image_file']
        # target.save(os.path.join(app.config['UPLOAD_FOLDER'], generate()))
        extension = target.filename.split('.')[1]
        random_filename = generate() + '.' + extension
        saved_filename = os.path.join(app.config['UPLOAD_FOLDER'], random_filename)
        
        
        target.save(saved_filename)


        key_hash = md5(key.encode('ascii')).digest()
        # Adjust key parity of generated Hash Key for Final Triple DES Key
        tdes_key = DES3.adjust_key_parity(key_hash)

        #  Cipher with integration of Triple DES key, MODE_EAX for Confidentiality & Authentication
        #  and nonce for generating random / pseudo random number
        cipher = DES3.new(tdes_key, DES3.MODE_EAX, nonce=b'0')

        # Open & read file from given path
        with open(saved_filename, 'rb') as input_file:
            file_bytes = input_file.read()

            if operation == '1':
                # Perform Encryption operation
               new_file_bytes = cipher.encrypt(file_bytes)
                
            else:
                # Perform Decryption operation
                new_file_bytes = cipher.decrypt(file_bytes)

        # Write updated values in file from given path
        with open(saved_filename, 'wb') as output_file:
           output_file.write(new_file_bytes)

        if(choice == '2'):
            return "/images/" + random_filename
        
        name = request.form['name']
        

        smtpObj = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port

        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.login(smtp_email, smtp_password)

        message = MIMEMultipart()
        message['From'] = smtp_email

        email = request.form['email']
        message['To'] = email
        
        message['Subject'] = name + " has sent you a document. "
        message['body'] = "You can decrypt the image at http://127.0.0.1:5000"
        
        with open(saved_filename, 'rb') as fp:
            img = MIMEImage(fp.read(), _subtype=False)
            img.add_header('Content-Disposition', 'attachment', filename=random_filename)
            message.attach(img)
            text = message.as_string()
            smtpObj.sendmail(smtp_email, email, text)
            
            

    return "Success"


if __name__ == '__main__':
    app.run(debug=True)
