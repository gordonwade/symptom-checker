# Symptom Checker App
#### Created by Gordon Wade
##### See live deployment at: [https://shielded-inlet-55288.herokuapp.com/](https://shielded-inlet-55288.herokuapp.com/)

## Background and Objective
This app is a proof-of-concept for a web application that aids in identification
of possible rare diseases. The project uses patient-supplied information about
symptoms to screen for possible rare disease matches.

### Technical Requirements
At a high level, the technical requirements are to build a single-page app that
fulfills the objective described above. Specifically, this means:
- Use [orphadata mapping](http://www.orphadata.org/data/xml/en_product4.xml)
of rare diseases and symptoms as a source of truth.
- Come up with a matching and scoring system using the above-mentioned data to
return the most relevant conditions for a set of symptoms.
- Setting up a Django server to process symptom queries as a `POST` request and
return the most likely disease matches.
- Layering a React frontend on top of this to serve as a responsive user
interface.

## Installation and Setup
As mentioned above, this app is based on Django and React, and will require
installations of Python and Node.js in order to develop and run.

#### Python Installation
Before starting, please ensure that you have a modern version of Python
accessible on your system. I used `Python 3.8.7` while developing this app.
- Set up a virtual environment. I used [`pyenv`](https://github.com/pyenv/pyenv#installation)
with [`pyenv-virtualenv`](https://github.com/pyenv/pyenv-virtualenv#installation)
for this, but there are many options. Your virtual environment creation command
may vary depending on which management tool you use. For me, it was:
```
pyenv virtualenv 3.8.7 symptom-checker-env
```
- Install the python requirements. Navigate to the top-level directory of this
repository, activate your virtual environment, and run:
```
pip install -r requirements.txt
```

#### Node.js Installation
- Ensure that you have an up-to-date installation of `node`. You can check
your version by running `node -v`. I used `v15.6.0` in development.
- Ensure that you have an up-to-date installation of `npm`. You can check
your version by running `npm -v`. I used version `7.9.0` in development.
- Install dependencies. At the root of the project (where `package.json`
is located), run `npm install`.
- Build the project. At the root of the directory, run `npm run build`

#### Django Setup
- Choose and set up a database for Django to use. The default is `SQLite`, but
I have chosen to use `PostgreSQL` for both local development and deployment.
- If using `PostgreSQL`, proceed to the next step. If using `SQLite` (or another
solution), please see the [Django documentation](https://docs.djangoproject.com/en/3.2/ref/settings/#databases)
and update the `DATABASES` entry in `settings.py` accordingly.
- Create a database and a user for this application. One set of instructions
for creating a `PostgreSQL` database and integrating it with Djanto can be found
[here](https://djangocentral.com/using-postgresql-with-django/).
- With the database name, user name, and password handy, proceed to the next
step (`Populate Environment Variables`).

...

- Once the database information has been successfully injected into the
environment, proceed with Django setup.
- From the project root, run `python manage.py makemigrations` followed by
`python manage.py migrate`. This should result in the database being created
by Django.
- I have written a few Django management commands to assist with setup. In order
to download the symptom-disease mapping and populate the database, run `python
manage.py populate_symptoms`
- Once this is done, the set of symptoms that will be presented to the user,
referred to as the "inclusion set" can be updated. This is currently done by
updating the `INCLUSION_IDS` variable in
`symptoms/management/commands/update_inclusion_set.py` to include the appropriate
symptom IDs. Once any changes have been made, run `python manage.py
update_inclusion_set` to propogate these changes to the database.
- If all has gone well, the Django portion of the app should now be ready!

#### Populate Environment Variables
This app relies on environment variables to specify important information, such
as database login parameters. In order to track and supply this information, I
use `.env` files. An example has been provided at `.example.env`, however `.env`
files with real parameters *should not be committed*, as they will likely 
contain secrets.
- Make a copy of `.example.env` and populate it with the correct information for
your deployment.
- Once this information is in place, export it in the console in which the server
will be run. There are many ways to do this - one option is `export $(xargs < .env)`

#### Run Locally
After following the previous setup instructions, the app can be run as-is:
- Start the Django app. At the root of the project, run `python manage.py runserver`.
- The app should now be viewable at [http://localhost:8000](http://localhost:8000).

In order to make changes to the React portion of the app, you will need to run
the development server: 
- Start the React app. At the root of the project, run `npm start`.
- The app should now be viewable at [http://localhost:3000](http://localhost:3000).
- After making the desired changes, the React app can be re-built with `npm run build`.
- The changes should now be viewable at [http://localhost:8000](http://localhost:8000)
without directly running the dev server.

## Implementation Details
This section will focus on additional implementation details.

#### Symptom-Disorder Matching
The matching of a set of provided symptoms to a set of possible disorders is the
core of the business logic for this application. This also extends to selecting
the set of symptoms that should be provided to the user initially.

##### Symptom Selection
After loading the symptom and disease information into the Django database, I
ran a few exploratory queries to help with this process.

The first step was to understand the relationships, which helpfully come with a
frequency mapping. In order to view the combinations, I ran the following:

```SQL
SELECT DISTINCT frequency_id, frequency_name FROM symptoms_symptomdisorder;
```
This generated a helpful table:

| frequency_id | frequency_name |   
| ------------ | -------------- | 
| 28433 | Very rare (<4-1%) |
| 28440 | Excluded (0%) |
| 28426 | Occasional (29-5%) |
| 28412 | Very frequent (99-80%) |
| 28419 | Frequent (79-30%) |
| 28405 | Obligate (100%) |

Next, I was interested to know hos many disorders were mapped to symptoms with
"obligate" frequency:

```SQL
SELECT term, COUNT(DISTINCT disorder_name)
FROM symptoms_disorder d
JOIN symptoms_symptomdisorder sd on d.id = sd.disorder_id_id
JOIN symptoms_symptom s on s.id = sd.symptom_id_id
WHERE sd.frequency_id in ('28405');
```
It turns out that while some symptoms are mapped to multiple conditions (up to
10), the general coverage of our disorder set would have been prohibitively low
for a symptom set of only 10 - 20 symptoms with this relationship frequency.

Next, I added in symptoms with "very frequent" occurrence, by changing the
`WHERE` clause: 
```SQL
WHERE sd.frequency_id in ('28405', '28412');
```
This gets us symptoms that correlate with a much larger number of diseases with
high frequency (up to a max of 396 disorders for one symptom).

I chose to base the initial "symptom selection" set on these results. The strength
of selecting symptoms this way is that we would be likely to find possible
matching diseases for any set of symptoms the user chose. The weakness is that
there may be substantial overlap between these most-frequent symptoms, which 
could make differentiating between possible disorders difficult.

##### Result Scoring
With an initial set of symptoms selected, the next question is how to find the
most relevant disorders for any given set of symptoms. One approach is to look
at the number of overlapping symptoms between a possible set for a disease and
the actual set provided by the user. I used this as a first implementation to
get the system working.

In order to improve these results, I decided to add "weighting" based on the
expected frequency of symptoms for a disease. In this system, an "obligate"
symptom would be worth 10 points, while a "frequent" symptom would be worth 6.
This is not the most sophisticated scoring system, but it does allow for
differentiation between disorders with high and low symptom occurrence.

Result scoring is one of the major areas for improvement in this application, as
explored in the "Future Directions" section. Possible ways to improve include:
- Adding more sophisticated logic to rule out disorders with "excluded" frequency
- Adding a "possible max" value that gives the maximum weighted match score based
on the set of symptoms from which the patient is choosing. This could be used
to more accurately score disorders where additional symptoms were present with
high likelihood, but were not selected by the user.
- Performing a more complete statistical analysis of the symptom overlap. This
could be used to select a symptom set that would provide greater possibility for
differentiating disorders with overlapping characteristics.
- Dynamically adjusting the available symptoms. Based on initial selections, the
user could be presented with different options for additional symptoms. These
could be selected by updating the likelihood after a given symptom is added to
the selection and using this to determine which additional symptoms are most
likely to co-occur.

## Testing
Testing has not yet been implemented for this application. In the future, three
areas should be addressed with tests.

#### Django API Testing
The Django API, which makes up the backend of this application should be tested
to ensure that it produces the expected results. These tests could include:
- Test of the `symptoms` endpoint to ensure that it returns the correct
"inclusion set" of symptoms for the user to select from.
- Test of the `disorder` endpoint with no symptom IDs selected, to ensure that
this returns no results.
- Test of the `disorder` endpoint with specific symptom IDs selected, to ensure
that the expected results are returned.
- Test of the `disorder` endpoint with invalid symptom IDs selected, to ensure
that no results are returned and/or that an error is raised.

#### React Interface Testing
To ensure that the frontend properly reflects the backend state and provides a
good user experience, testing of React components should also be included. This
could involve:
- Ensuring that all components are correctly rendered when the pages is first
accessed.
- Attempting a valid submission and ensuring that new components are rendered
to display the results.
- Attempting an invalid submission and ensuring that an appropriate alert or
error message is triggered.

#### Business Logic Testing
To ensure that users are being presented with correct information, some use
cases should be identified along with expected results. These can then be tested
via the Django API to ensure that the logic is functioning properly.

## Deployment Details
A live version of this app is available at [https://shielded-inlet-55288.herokuapp.com/](https://shielded-inlet-55288.herokuapp.com/).
As the URL suggests, this is hosted through Heroku. It is currently served on
the free tier, meaning the `dyno` sleeps after 15 minutes of activity. In order
to reduce wait time, please click the link and allow the `dyno` to wake while
you finish reading this section!

In order to support the live deployment of this app, I created an AWS RDS instance
running PostgreSQL to act as the database.

In a production deployment, there would be additional factors to consider,
including custom domains, uptime monitoring, security, etc. but I have chosen
to keep this as simple as possible for the proof of concept.

## Future Directions
There are several potential improvements for this application, which can be
prioritized depending on the ultimate goal. A few possibilities are:
- **Include links to symptom detail pages when the user is presented with their
results.** In the current implementation, each result card has a `Learn More`
button, which is disabled. In a future update, these could direct the user to
pages with more information about the disease in order to better inform them.
- **Implement more advanced symptom-disease matching.** The current system relies
primarily on a "score" which is generated by weighting the chosen symptoms on
the "frequency" of association with each disease.

    This weighting provides a good basis for symptom-disease association, but
    does not fully take into account the fact that the user is provided with a
    limited set of symptoms to choose from. It also does not take into account
    some symptoms that could rule a disease out based on their presence or absence.
 
- **Set up user account management.** It could be helpful to allow users to 
create accounts so their information can be saved. This would also allow
collection of contact information, which could be used to provide information
or alerts when disease updates become available.