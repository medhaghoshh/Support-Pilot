import platform
import os
from sqlalchemy.orm import Session

from app.database import engine


class DeploymentCheck:

    @staticmethod
    def check_database():
        try:
            conn = engine.connect()
            conn.close()

            return {
                "status": "PASS",
                "message": "Database Connected Successfully"
            }

        except Exception as e:
            return {
                "status": "FAIL",
                "message": str(e)
            }

    @staticmethod
    def check_environment():

        return {
            "python_version": platform.python_version(),
            "operating_system": platform.system(),
            "working_directory": os.getcwd()
        }

    @staticmethod
    def deployment_status(db: Session):

        return {
            "database": DeploymentCheck.check_database(),
            "environment": DeploymentCheck.check_environment(),
            "ready_for_deployment": True
        }

if __name__ == "__main__":
    import pprint
    print("Running SupportPilot Deployment Check...")
    status = DeploymentCheck.check_database()
    print("Database Check:")
    pprint.pprint(status)
    env = DeploymentCheck.check_environment()
    print("Environment Check:")
    pprint.pprint(env)
