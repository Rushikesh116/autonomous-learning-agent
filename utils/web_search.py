from langchain_community.tools.tavily_search import TavilySearchResults

def web_search(query):
    search = TavilySearchResults(k=3)
    return search.invoke(query)