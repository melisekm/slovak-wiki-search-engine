# Slovak Wiki parser, indexer and search engine
Archived.

## Description
Parse, index and search on *slovak* wiki  
Language: Python  
Data: Slovak wiki dump `wiki-latest-pages-articles.xml`, size 1.42 GB

- Preprocess text with NLP, normalize, tokenize, remove stopwords, POS tagging, lemmatization.
- Create inverted index and precompute tf-idf
- User enters query in a form of natural question => Kto je prezidentom Slovenskej republiky? => prezident AND Slovenský AND Republika.
Or an OR query.
- Program return N (parameter) most relevant documents (intersection if AND, union if OR)
- Calculate tf-idf, cosine similarity between query and relevant documents, sort results and show them to user
- Among the returned results additional structued data from infoboxes are parsed

## Structure

Program is separated to three parts.
1. Custom implementation of preprocessing and indexing. (slovak_wiki_search_engine) - not dockerized
2. Spark distributed implementation of preprocessing. (spark) - dockerized
3. PyLucene implementation of indexing and searching. (pylucene) - dockerized