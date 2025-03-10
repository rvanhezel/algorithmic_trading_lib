from src.strategys.abstract_strategy import AbstractStrategy
from src.services.market_data_service import MarketDataService
from src.execution.configuration import Configuration
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
import requests
from bs4 import BeautifulSoup
import re
import logging
from src.utilities.enums import Signal
import pandas as pd
from src.utilities.utils import timezone_from_calendar
from src.readers.alpha_vantage_mkdata_api import AlphaVantageAPI


class BERTBasedSentimentStrategy(AbstractStrategy):

    @staticmethod
    def generate_signals(mkdata_service: MarketDataService, tickers: list[str], cfg: Configuration) -> dict[str, Signal]:     
        """We compare whether the news today was better than yesterday. If so buy, if not sell. Hold if no change."""   
        logging.info(f"Generating signals using {__class__.__name__}")
        signals = {}

        now = pd.Timestamp.now(tz=timezone_from_calendar(cfg.market))
        today = now.normalize()
        yesterday = now - pd.Timedelta(days=1)
        yesterday_eod = pd.Timestamp(yesterday.year, yesterday.month, yesterday.day, 16, 0, tz=timezone_from_calendar(cfg.market))

        for ticker in tickers:

            news = mkdata_service.get_news(cfg.market_data_api, "TSLA", today, now)
            yesterdays_news = mkdata_service.get_news(cfg.market_data_api, "TSLA", yesterday, yesterday_eod)

            classifier = pipeline('sentiment-analysis')
            news['DistilBERT_sentiment'] = news['summary'].apply(lambda x: classifier(x)[0]['label'])
            yesterdays_news['DistilBERT_sentiment'] = yesterdays_news['summary'].apply(lambda x: classifier(x)[0]['label'])

            tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
            model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')

            def get_pt_score(review):
                tokens = tokenizer.encode(review, return_tensors='pt')
                result = model(tokens)
                return int(torch.argmax(result.logits))+1

            news['BERT_pt_sentiment'] = news['summary'].apply(lambda x: get_pt_score(x))
            yesterdays_news['BERT_pt_sentiment'] = yesterdays_news['summary'].apply(lambda x: get_pt_score(x))

            # today avg
            nrows = news.shape[0]
            positive_count = news['DistilBERT_sentiment'].value_counts().get('POSITIVE', 0)
            values_above_3_count = (news['BERT_pt_sentiment'] > 3).sum()
            avg_positive = (positive_count + values_above_3_count) / (2 * nrows)

            msg = f"{ticker} has {(positive_count + values_above_3_count) / 2} out of {nrows} articles with positive sentiment"
            logging.debug(msg)

            # yesterday avg
            yesterday_nrows = yesterdays_news.shape[0]
            yesterday_positive_count = yesterdays_news['DistilBERT_sentiment'].value_counts().get('POSITIVE', 0)
            yesterday_values_above_3_count = (yesterdays_news['BERT_pt_sentiment'] > 3).sum()
            yesterday_avg_positive = (yesterday_positive_count + yesterday_values_above_3_count) / (2 * yesterday_nrows)

            msg = f"Yesterday {ticker} had {(positive_count + values_above_3_count) / 2} out of {nrows} articles with positive sentiment"
            logging.debug(msg)

            if avg_positive > yesterday_avg_positive:
                signal = Signal.BUY
            elif avg_positive < yesterday_avg_positive:
                signal = Signal.SELL
            else:
                signal = Signal.HOLD

            logging.info(f"Sentiment signal for {ticker}: {signal}")
            signals[ticker] = signal




