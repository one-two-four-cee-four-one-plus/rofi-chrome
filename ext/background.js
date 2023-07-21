var port = chrome.runtime.connectNative('com.my_extension.my_native_host');

function dump_tab(tab) {
    return {title: tab.title, id: tab.id, url: tab.url}
}

function ping() {
    setTimeout(_ => {
        port.postMessage({ type: 'ping' });
        ping();
    }, 10000);
}

port.onMessage.addListener((response) => {
    console.log(JSON.stringify(response));
    if (response.type == 'close') {
        chrome.tabs.remove(response.data);
    } else if (response.type == 'switch') {
        chrome.tabs.update(response.data, {active: true});
    } else if (response.type == 'open') {
        chrome.tabs.create({url: `https://duckduckgo.com/?q=${encodeURIComponent(response.data)}`});
    } else if (response.type == 'goto') {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            let currTab = tabs[0];
            if (currTab) {
                chrome.tabs.update(
                    currTab.id,
                    {url: `https://duckduckgo.com/?q=${encodeURIComponent(response.data)}`}
                );
            }
        });
    } else if (response.type == 'tabs') {
        chrome.tabs.query({}, function(tabs) {
            port.postMessage({type: 'tabs', data: tabs.map(dump_tab)});
        });
    }
});

ping();
