from app import app, db
from app.models import Employer, Employee, Review

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Employer': Employer, 'Employee': Employee, 'Review': Review}