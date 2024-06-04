var province_items = document.querySelectorAll("a.省份");
var city_items = document.querySelectorAll("a.城市");

var current_province = document.querySelector("button.省份");
var current_city = document.querySelector("button.城市");
if (current_province && current_province.textContent == "全部") {
    current_province = null;
}
if (current_city && current_city.textContent == "全部") {
    current_city = null;
}

// clear city filter while selecting province filter
for (var i = 0; i < province_items.length; i++) {
    var item = province_items[i];
    var url = new URL(item.href);
    url.searchParams.set("city", "");
    item.href = url.href;
}

// replace province name in city filter
let check_province = (name) => {
    if (!name) {
        return;
    }
    if (current_province && name.textContent == current_province.textContent) {
        name.textContent = "省级平台";
    }
}
check_province(current_city)
for (var i = 0; i < city_items.length; i++) {
    var item = city_items[i];
    check_province(item);
}

var all_items = document.querySelectorAll("a.dropdown-item");
for (var i = 0; i < all_items.length; i++) {
    var item = all_items[i];
    var url = new URL(item.href);
    item.href = `${url.pathname}${url.search}`;
}
