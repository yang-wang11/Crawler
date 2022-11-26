# -*- coding: utf-8 -*-

import time
import traceback
from crawler import GeekCrawler
from util import GetLogger

if __name__ == "__main__":

    logger = GetLogger()

    try:

        geek = GeekCrawler(logger=logger)
        geek.get_products()  # 请求获取课程接口

        count = 0
        for product in geek.products:

            geek.get_articles(product)  # 获取文章列表

            article_ids = product['article_ids']

            for aid in article_ids:

                if str(aid) in geek.finished_articles:
                    logger.info(f"{aid}已经抓取完成，跳过。")
                    continue

                geek.get_article(aid, product)  # 获取单个文章的信息

                time.sleep(5)  # 做一个延时请求，避免过快请求接口被限制访问

                count += 1
                if count >= 5:
                    logger.info("抓取超过阈值，暂停10s后继续。")
                    time.sleep(10)
                    count = 0  # 重新计数
                    geek.refresh_auth()

        logger.info("抓取完成。")

    except Exception as e:

        logger.error(f"请求过程中出错了，出错信息为：{e}:{traceback.format_exc()}")
