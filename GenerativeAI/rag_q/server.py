from dotenv import load_dotenv
from fastapi import FastAPI,Query
from .client.rq_client import queue
from .queues.worker import process_query

load_dotenv()
app=FastAPI()

@app.get('/')
def root():
    return{'status':'Server is up and Running'}


@app.post('/chat')
def chat(
    query:str=Query(...,discription="The chat query of the user")
):
    job=queue.enqueue(process_query,query)
    return {"status":"queued","job_id":job.id}

@app.get('/job_status')
def get_result(
        job_id:str=Query(...,discription="Job id")
):
    job=queue.fetch_job(job_id=job_id)
    result=job.return_value()

    return {"result":result}

