xpath_selectors = {
    "pages": '//a[@data-qa="pager-next"]/@href',
    "vacancy": '//a[@data-qa="vacancy-serp__vacancy-title"]/@href',
    "author": '//a[@data-qa="vacancy-company-name"]/@href'
}

xpath_vacancy_data_selectors = {
    "title": "//h1//text()",
    "price": "//p[@class='vacancy-salary']/span/text()",
    "description": "//script[@type='application/ld+json']/text()",
    "tags": "//span[@data-qa='bloko-tag__text']/text()",
    "author": '//a[@data-qa="vacancy-company-name"]/@href'
}

xpath_author_data_selectors = {
    "title": "//div[@class='company-header']//h1//text()",
    "website": "//a[@data-qa='sidebar-company-site']/@href",
    "activity": "//div[@class='employer-sidebar-block']/p/text()",
    "description": "//div[@data-qa='company-description-text']//text()",
    "vacancies": "//a[@data-qa='vacancy-serp__vacancy-title']/@href",
}
