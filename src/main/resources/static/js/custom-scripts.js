var province_items = document.getElementsByClassName("省份");

for (var i = 0; i < province_items.length; i++) {
    var url = new URL(province_items[i].href);
    url.searchParams.set('city', '');
    province_items[i].href = url.href;
}
