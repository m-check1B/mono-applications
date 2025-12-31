import os
import pathlib
base = pathlib.Path(__file__).parent
os.environ['DATABASE_URL']='sqlite:///'+str(base/'tmp_test.db')
os.environ['TEST_DATABASE_URL']=os.environ['DATABASE_URL']
os.environ['SKIP_DB_INIT']='1'
from app.core.database import Base
# import models to register tables
import app.models.user
import app.models.task
import app.models.session
import app.models.event
import app.models.time_entry
import app.models.voice_recording
import app.models.workflow_template
import app.models.ai_conversation
import app.models.shadow_profile
import app.models.item_type
import app.models.knowledge_item
import app.models.workspace
import app.models.command_history
import app.models.agent_session
import app.models.file_search_document
import app.models.file_search_store
import app.models.request_telemetry
from sqlalchemy import create_engine
engine = create_engine(os.environ['DATABASE_URL'], connect_args={'check_same_thread': False})
Base.metadata.create_all(engine)
print('create_all success')
