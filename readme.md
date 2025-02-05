# NextGenVoting - How to Use and Install

## Installation and Setup

### 1. Install Python and Django
Make sure Python is installed on your system. Then, install Django.

```bash
pip install django
```

### 2. Start Virtual Environment
if there is a file in this project named venv, 
then use this command to start it:
```bash
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows (Command Prompt)
```

if there is no venv, then create one with this command:
```bash
python -m venv venv
```

and then activate it with the first command

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration
- Ensure there is a `.env` file in the project root.
- The only empty part should be the database password.
- Create a Django superuser and remember the password:

```bash
python manage.py createsuperuser
```
---

## PostgreSQL Setup

### 1. Install PostgreSQL
Download and install PostgreSQL from the [website](https://www.postgresql.org/download/).

![PostgreSQL Installation](path/to/postgres-install-image.png)

### 2. Create the Database
Open PostgreSQL and create a new database named `local_nextgenvoting`.

```sql
CREATE DATABASE local_nextgenvoting;
```
You will be prompted to create a password. 
Store the database password in the `.env` file.

![Creating Database](path/to/database-create-image.png)

---

## Running the Project

### 1. Start the Django Server
```bash
python manage.py runserver
```

### 2. Start Redis
Ensure Redis is running before starting Celery.

```bash
redis-server
```

### 3. Start Celery
```bash
celery -A nextgenvoting worker 
```

![Running the Server](path/to/server-running-image.png)

---

## Usage
goto localhost on your browser
```
localhost:8000/
```


### 1. Sign Up
Go to the login page and signin with your superuser details.

![Signup Page](path/to/signup-image.png)

### 2. Create a CSV File for voters, you can use your own email. 
Prepare a CSV file with `name` and `email` headers and upload it.

```csv
name,email
John Doe,john@example.com
Jane Smith,jane@example.com
```

![Uploading CSV](path/to/csv-upload-image.png)

### 3. Create an Election
Fill out the election details, including the number of ballots, voting type, and candidates.

![Creating Election](path/to/election-create-image.png)

### 4. Start the Election
Once everything is set up, start the election. Voters will receive an email with a unique link to vote.

![Starting Election](path/to/start-election-image.png)

### 5. End the Election
After voting is complete, end the election to count the votes.

![Ending Election](path/to/end-election-image.png)

---

## Testing

### 1. Run a Mock Election
To test the system, you can run a mock election with sample data:

```bash
python manage.py generate_votes <VOTES> <CANDIDATES> <WINNERS>
```

![Mock Election](path/to/mock-election-image.png)

---



