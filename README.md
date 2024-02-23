# Tekkiez
## Video Demo: https://youtu.be/Yb_ScPgQPTQ
## Description:
Tekkiez is a web application whose purpose is to connect Home owners with caretakers who can take care of their properties.
## Languages Used:
HTML5, CSS3, JavaScript, Bootstrap5, and Flask.
## Components
The Authentication, Home Page, The Home Owner module, and the Caretaker module.
## Implementation Details
## Overall Logic
In general, home owners post their properties, then caretakers apply to care for those properties.
## Design Decisions
The main design decision was how to store the images in the application.\
Initially, I had decided to store them as a blob object in the database. This however proved to be inefficient since after storage of many pictures in the database, its overall performance would reduce. Conversion of blob to a viewable image file would also be complicated.\
After doing a bit of research, I decided to store the images in the static section of the app then store the names of the images in the database.\
In order to avoid a situation whereby two images belonging to different users are stored using the same names, random numbers are prepended to the image filenames.
## Website Layout
The layout of most pages in the application is defined in "layout.html".\
The layout file includes Bootstrap links for the stylesheet, icons, and JavaScript. It also includes the link to the website where the favicon was obtained from.
## Authentication
### _Registration_
Route(s): "/register"\
Template(s): "register.html"\
On the registration page, a user must provide the following details: full name, email address, account type, address, ID number, Date of Birth, and password.\
Once submitted the details are stored in the database. The only thing stored in a unique way is the password since its hash is what is stored in the database.
### _Log In_
Route(s): "/login"\
Template(s): "login.html"\
In order to log in, a user must provide their email address, their account type, and their password.\
This is compared to the data stored in the database and if a match is found, the user is logged in to the system.
### _Log Out_
Route(s): "logout"\
When a user clicks the logout button, the session_variable is cleared.
## Home Page
Route(s): "/"\
Template(s): "index.html"\
The template welcomes users to the website an gives information regarding the number of properties advertised on the website, the number of caretakers available and the number of jobs provided. This is done by obtaining the count of properties, caretakers, and jobs provided from the database.
## Caretaker Module
The Caretaker Module consists of four key parts: Dashboard, My Profile, Apply for Jobs, and View Applications.
### _Dashboard_
Route(s): "/ctdashboard"\
Template(s): "ctdashboard.html"\
A caretaker's dashboard contains two key pieces of information: The number of jobs they can apply for as well as the number of applications they've already made.\
This information is obtained using the "/ctdashboard" route in app.py. Here, the number of properties and the number of applications made by the caretaker are obtained from the database. It is only the properties that haven't got a caretaker that are counted.
### _My Profile_
Route(s): "/ctprofile"\
Template(s): "ctprofile.html"\
A caretaker's profile consists of their: full name, email address, account type, ID number, date of birth, address, personal statement, and a profile picture.\
When they first create an account, the personal statement and profile picture are usually not included in registration. In order for a caretaker to be able to apply for jobs, they have to first complete their profile by adding a personal statement, a scanned copy of their ID, and profile picture.\
Once the profile is complete, the address, personal statement and profile statement remain changeable.
### _Apply for Jobs_
Route(s): "/ctapplication", "/ctapplicationpage"\
Template(s): "ctapplication.html", "ctapplicationpage.html"\
In the Job application section, all the available properties are displayed.\
The following details about the property are displayed: a picture of the property, the property name, the date on which it was posted, the property's description, and it's location.\
The properties are obtained from the database through the "/ctapplication" route. All the properties are then iteratively displayer.\
When a caretaker clicks the apply button next to a property, it takes them to application page for the selected property. This page includes all the pictures of the property, the job description, as well as a space for the caretaker to explain why they are the perfect fit for the role.
### _View Applications_
Route(s): "/ctapplicationsmade"\
Template(s): "ctapplicationsmade.html"\
In the applications view page, the caretaker is able to view and modify all the applications they've made.\
The caretaker is able to see a picture of the property, the name of the property, the date of application, the property's description, and the status of the application.\
Next to each application, there's a cancel button for cancellation of any previously made applications. Only pending applications can be cancelled.
## Homeowners Module
### _Dashboard_
Route(s): "/hdashboard"\
Template(s): "hdashboard.html"\
A home owner's dashboard contains two key pieces of information: The number of properties they've posted as well as the number of applications pending their approval or rejection.\
This information is obtained using the "/hdashboard" route in app.py. Here, the number of properties and the number of applications made by the caretakers are obtained from the database.
### _Post Property_
Route(s): "/postproperty"\
Template(s): "postproperty.html"\
This page is used by home owners for posting their properties.\
The following information must be provided: property name, description, location, tasks required to be performed on the property, and a picture of the property. Upto five pictures can be posted, only the first picture is mandatory.
### _Property Management_
Route(s): "/hpropertymanagement", "/hpropertyview"\
Template(s): "hpropertymanagement.html", "hpropertyview.html"\
On this page, a home owner is able to see all the properties they have posted.\
The property details shown are: a picture of the property, the property name, description, and location.\
The home owner can then decide to view/modify the property by clicking on the "view/modify" button. On clicking this button it opens up a new page that displays more details of the selected property. On this page, the home owner can view all the images of their property and modify if they wish.
### _Applications Management_
Route(s): "/happlicationmanagement", "/happlicationsview"\
Template(s): "happlicationmanagement.html", "happlicationsview.html"\
On this page, a home owner is able to see applications made by various caretakers to their properties.\
They are able to see the following: a picture of the property, the name of the property being applied for, the name of the applying caretaker, and their profile photo.\
On clicking the view button next to the caretaker's profile photo, they are able to view the application in detail. In addition to the details on the first page, they are also able to see the reason the caretaker gave of why they would be the best fit for the job.\