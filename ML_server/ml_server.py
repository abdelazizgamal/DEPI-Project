import os
import json
import socket
from queue import Queue
from threading import Thread
import pandas as pd
import google.generativeai as genai
from numpy.ma.core import product
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy import signals
from scrapy.signalmanager import dispatcher
from scraper.scraper.spiders.AmazonScraping import AmazonSpider
from sentiment_analyzer import analyze_sentiment, get_pros_cons, get_summary
from multiprocessing import Process, Queue as MPQueue


def run_spider(urls, results_queue):
    results = []

    def item_scraped(item, response, spider):
        print(f"Item scraped: {item}")  # Add logging
        results.append(item)

    def spider_closed(spider):
        print(f"Spider closed. Total items scraped: {len(results)}")  # Add logging
        df = pd.DataFrame(results)
        if df.empty:
            print("Warning: DataFrame is empty!")  # Add warning
        else:
            print(f"DataFrame info:\n{df.info()}")  # Add DataFrame info logging
        results_queue.put(df)

    process = CrawlerProcess(get_project_settings())
    dispatcher.connect(item_scraped, signal=signals.item_scraped)
    dispatcher.connect(spider_closed, signal=signals.spider_closed)

    try:
        process.crawl(AmazonSpider, start_urls=urls)
        process.start()
    except Exception as e:
        print(f"Error during crawling: {str(e)}")  # Add error logging
        results_queue.put(pd.DataFrame())  # Put an empty DataFrame in case of error


def spider_process(urls, results_queue):
    run_spider(urls, results_queue)


def process_request(request):
    urls = [request]
    results_queue = MPQueue()

    p = Process(target=spider_process, args=(urls, results_queue))
    p.start()
    data = results_queue.get()
    p.join()

    print(data.info())
    print(data.head(5))

    if data.empty:
        print("Warning: Scraped data is empty!")
        return {
            "product": request,
            "error": "No data was scraped. Please check the URL and try again."
        }

    if data.empty:
        print("Warning: Scraped data is empty!")
        return {
            "product": request,
            "error": "No data was scraped. Please check the URL and try again."
        }

    sentiment_result = analyze_sentiment(data)
    genai.configure(api_key=os.environ['GENAI_API_KEY'])
    pros, cons, summary = get_pros_cons(sentiment_result)
    positive_reviews = sum(sentiment_result['predicted_rating'] == 1)
    negative_reviews = sum(sentiment_result['predicted_rating'] == 0)

    product = data['product'][0]
    price = data['price'][0]
    avg_rating = data['avg_rating'][0]

    return {
        "product": product,
        "price": price,
        "pros": pros,
        "cons": cons,
        "summary": summary,
        "avg_rating": avg_rating,
        "positive_reviews": positive_reviews,
        "negative_reviews": negative_reviews,
    }


def handle_client(client_socket):
    request = client_socket.recv(1024).decode()
    print(f"Received request: {request}")

    result = process_request(request)

    client_socket.send(json.dumps(result).encode())
    client_socket.close()


def start_server(host='0.0.0.0', port=5000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"[*] Listening on {host}:{port}")

    while True:
        client, addr = server.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
        client_handler = Thread(target=handle_client, args=(client,))
        client_handler.start()


if __name__ == "__main__":
    start_server()