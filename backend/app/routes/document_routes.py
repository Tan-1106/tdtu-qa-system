from bson import ObjectId
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException

from app.models.document import Document
from app.database.mongo import get_documents_collection
from app.utils.api_response import success_response, error_response

router = APIRouter()

# Helper function to convert MongoDB document to dict
def doc_helper(doc) -> dict:
    return {
        "id": str(doc["_id"]),
        "title": doc["title"],
        "source": doc["source"],
        "uploaded_by": doc.get("uploaded_by"),
        "created_at": doc["created_at"].isoformat() if "created_at" in doc else None
    }
    
# Route to create a new document
@router.post("/", response_model=dict)
async def create_document(document: Document):
    try:
        documents = get_documents_collection()
        doc = document.model_dump(by_alias=True, exclude={"id"})
        result = await documents.insert_one(doc)
        created_doc = await documents.find_one({"_id": result.inserted_id})
        if not created_doc:
            raise HTTPException(status_code=500, detail="Failed to fetch created document")

        resp, code = success_response(
            data=doc_helper(created_doc),
            message="Document created",
            status_code=201
        )
        return JSONResponse(content=resp, status_code=code)

    except Exception as e:
        resp, code = error_response(message=f"Error creating document: {str(e)}", status_code=500)
        return JSONResponse(content=resp, status_code=code)
    
# Route to get all documents
@router.get("/", response_model=dict)
async def get_all_documents():
    try:
        documents = get_documents_collection()
        cursor = documents.find()
        docs = []
        async for doc in cursor:
            docs.append(doc_helper(doc))

        resp, code = success_response(
            data=docs,
            message="Fetched all documents",
            status_code=200
        )
        return JSONResponse(content=resp, status_code=code)

    except Exception as e:
        resp, code = error_response(message=f"Error fetching documents: {str(e)}", status_code=500)
        return JSONResponse(content=resp, status_code=code)
