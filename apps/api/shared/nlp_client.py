from google.cloud import language_v2

class SentimentResult:
    def __init__(self, score: float, magnitude: float):
        self.score = score
        self.magnitude = magnitude

class EntityResult:
    def __init__(self, name: str, type_: str, salience: float):
        self.name = name
        self.type = type_
        self.salience = salience

async def analyze_sentiment(text: str) -> SentimentResult:
    """Analyze sentiment of text using Cloud Natural Language API."""
    client = language_v2.LanguageServiceClient()
    document = language_v2.Document(
        content=text,
        type_=language_v2.Document.Type.PLAIN_TEXT,
    )
    # Using synchronous call in a thread pool for async wrapper (or just sync call here, since GCP standard clients are often sync)
    # Since we need async everywhere, we'll wrap it in asyncio.to_thread
    import asyncio
    
    def _call():
        return client.analyze_sentiment(
            request={"document": document}
        )
        
    response = await asyncio.to_thread(_call)
    return SentimentResult(
        score=response.document_sentiment.score,
        magnitude=response.document_sentiment.magnitude
    )

async def extract_entities(text: str) -> list[EntityResult]:
    """Extract entities from text using Cloud Natural Language API."""
    client = language_v2.LanguageServiceClient()
    document = language_v2.Document(
        content=text,
        type_=language_v2.Document.Type.PLAIN_TEXT,
    )
    
    import asyncio
    def _call():
        return client.analyze_entities(
            request={"document": document}
        )
        
    response = await asyncio.to_thread(_call)
    
    entities = []
    for entity in response.entities:
        entities.append(EntityResult(
            name=entity.name,
            type_=language_v2.Entity.Type(entity.type_).name,
            salience=entity.salience
        ))
    return entities
