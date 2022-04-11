xpath_selectors = {
    "pages": '//a[@class="pagination-page"]/@href',
    "flat": '//a[@data-marker="item-title"]/@href'
}

xpath_data_selectors = {
    "title": "//h1/span/text()",
    "price": "//div[@class='item-view-content-right']//span[@itemprop='price']/text()",
    "address": "//span[@class='item-address__string']/text()",
    "parameters": "//div[@class='item-params']//li//text()",
    "author": "//div[@class='item-phone-seller-info']//div[@data-marker='seller-info/name']/a/@href",
}
