from langchain_openai.chat_models import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.runnables import RunnableSequence, RunnableLambda
from langchain_core.prompts import PromptTemplate, HumanMessagePromptTemplate
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional, Literal, Callable, Union
from langchain_core.callbacks.stdout import StdOutCallbackHandler
import os
import json

_ = load_dotenv('.env')


class AIAssistant:
    
    # TYPING OF MODELS
    TYPES_OPEN_AI_MODELS = Literal["gpt-4o-mini","gpt-4o","o1-mini-preview","o1-preview"]
    TYPES_META_MODELS = Literal["LLaMa-3.1", "LLaMa-3.2", "llama-3.1-70b-versatile"]
    TYPES_ANTHROPIC_MODELS = Literal["claude-3-5-sonnet-latest", "claude-3-5-haiku-latest"]
    
    # STRINGS OF MODELS
    OPEN_AI_MODELS = {"gpt-4o-mini","gpt-4o","o1-mini-preview","o1-preview"}
    META_MODELS = {"LLaMa-3.1", "LLaMa-3.2", "llama-3.1-70b-versatile"}
    ANTHROPIC_MODELS = {"claude-3-5-sonnet-latest", "claude-3-5-haiku-latest"}

    Models = Union[TYPES_OPEN_AI_MODELS, TYPES_META_MODELS]

    @classmethod
    def create_ai_client(cls, *, model : Models, temperature : float = 0.0, **model_kwargs : dict[str, str]) -> ChatOpenAI:
        # if model in cls.META_MODELS:
            return ChatGroq(api_key=os.environ.get("GROQ_API_KEY"), model_name=model)
        # elif model in cls.ANTHROPIC_MODELS:return ChatAnthropic(model='claude-3-opus-20240229', temperature=temperature, api_key=os.environ.get("ANTHROPIC_API_KEY"), **model_kwargs)
        # return ChatOpenAI(model = model, temperature = temperature, api_key=os.environ.get("OPENAI_API_KEY"), **model_kwargs)
        

    def __init__(self, 
                prompt_template : str, 
                model_str : Models,
                temperature : float = 0.0,
                **kwargs : dict[str, str]
            ) -> None:
        self.Prompt = PromptTemplate.from_template(prompt_template)
        self.Model = AIAssistant.create_ai_client(model = model_str, temperature = temperature, **kwargs)
        self.chat_history_messages = []
        [setattr(self, k,v ) for k, v in kwargs.items()]

    def create_chain(self, callables_and_output_parsers : list[Callable, BaseModel] | None) -> RunnableSequence:
        if not callables_and_output_parsers:return RunnableSequence(*[self.Prompt, self.Model, StrOutputParser()])
        return RunnableSequence(*[
            self.Prompt, 
            self.Model, 
                *[
                    PydanticOutputParser(pydantic_object=obj) 
                    if issubclass(obj, BaseModel)
                    else RunnableLambda(obj)
                    for obj in callables_and_output_parsers
                ],
            ]
        )

    def chat(self, message : dict[str, str], callables_and_output_parsers : list[Callable | BaseModel] | None = None) -> str:
        chain = self.create_chain(callables_and_output_parsers)
        response = chain.invoke(message, config={'callbacks': [StdOutCallbackHandler()]})
        self.chat_history_messages.append(("user", message))
        self.chat_history_messages.append(("ai", response))
        return response
    
if __name__ == "__main__":
    # chatbot = AIAssistant(
    #     "Mi chiamo {name}. Aiutami a scrivere un tema sull'argomento {argomento}", 
    #     model_str="gpt-4o-mini"
    #     # model_str="claude-3-5-haiku-latest"
    # )
    # result = chatbot.chat({"name" : "Giovanni", "argomento" : "seconda guerra mondiale"})
    # print(result)


    chatbot = AIAssistant(
        """
        Ti passo dei 2 dei 3 dati di un triangolo. 
        Dimmi se è una terna pitagorica, e calcola l'ultimo lato. 
        Restituisci in un json la risposta.
        Il json è composto così:
        {{
            "cateto_1" : <un valore opzionale che estrai dai dati. tipo float>, 
            "cateto_2" : <un valore opzionale che estrai dai dati. tipo float>,
            "ipotenusa" : <un valore opzionale che estrai dai dati. tipo float>,
            "corretta" : <un valore opzionale che decidi tu. Tipo booleano o None>
        }}
        se non trovi dai dati il terzo lato, lascia il campo vuoto, e metti null sulla corretezza dell'ipotenusa
        {data}""", 
        model_str="gpt-4o-mini"
        # model_str="claude-3-5-haiku-latest"
    )

    class TernaPitagorica(BaseModel):
        cateto_1 : Optional[float]
        cateto_2 : Optional[float]
        ipotenusa : Optional[float]
        corretta : Optional[bool]
    
    def calculate_third_lato(data : dict[Literal["cateto_1", "cateto_2", "ipotenusa"], float])-> dict:
        if "cateto_1" in data and "cateto_2" in data:
            data["ipotenusa"] = (data["cateto_1"]**2 + data["cateto_2"]**2)**0.5
        elif "cateto_1" in data and "ipotenusa" in data:
            data["cateto_2"] = (data["ipotenusa"]**2 - data["cateto_1"]**2)**0.5
        elif "cateto_2" in data and "ipotenusa" in data:
            data["cateto_1"] = (data["ipotenusa"]**2 - data["cateto_2"]**2)**0.5
        return data
    
    result = chatbot.chat(
        {"data" : "cateto 1 : 3, cateto 2 : 4"},
        # [
            # TernaPitagorica, 
            # calculate_third_lato
        # ]
    )
    print(result)