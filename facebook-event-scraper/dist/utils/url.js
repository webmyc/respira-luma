"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.validateAndFormatEventGroupUrl = exports.validateAndFormatEventProfileUrl = exports.validateAndFormatEventPageUrl = exports.validateAndFormatUrl = exports.fbidToUrl = void 0;
const enums_1 = require("../enums");
const fbidToUrl = (fbid) => {
    if (!fbid.match(/^[0-9]{8,}$/)) {
        throw new Error('Invalid FB ID');
    }
    return `https://www.facebook.com/events/${fbid}?_fb_noscript=1`;
};
exports.fbidToUrl = fbidToUrl;
// Covers events with the following format:
// https://www.facebook.com/events/666594420519340/
// https://www.facebook.com/events/shark-tank-pub/80s-90s-00s-night/2416437368638666/
// https://www.facebook.com/events/1137956700212933/1137956706879599/ (recurring events)
const validateAndFormatUrl = (url) => {
    var _a;
    const fbid = (_a = url.match(/facebook\.com\/events\/(?:.+\/.+\/)?([0-9]{8,})/)) === null || _a === void 0 ? void 0 : _a[1];
    if (!fbid) {
        throw new Error('Invalid Facebook event URL');
    }
    return `https://www.facebook.com/events/${fbid}?_fb_noscript=1`;
};
exports.validateAndFormatUrl = validateAndFormatUrl;
// Covers pages with the following format:
// https://www.facebook.com/lacalle8prague/past_hosted_events
// https://www.facebook.com/lacalle8prague/upcoming_hosted_events
// https://www.facebook.com/lacalle8prague/events
const validateAndFormatEventPageUrl = (url, type) => {
    const regex = /facebook\.com\/[a-zA-Z0-9]+(?:\/(past_hosted_events|upcoming_hosted_events|events))?$/;
    const result = regex.test(url);
    if (!result) {
        throw new Error('Invalid Facebook page event URL');
    }
    const types = /(past_hosted_events|upcoming_hosted_events|events)$/;
    if (!types.test(url)) {
        if (type === enums_1.EventType.Past) {
            url += '/past_hosted_events';
        }
        else if (type === enums_1.EventType.Upcoming) {
            url += '/upcoming_hosted_events';
        }
        else {
            url += '/events';
        }
    }
    else if (type === enums_1.EventType.Past) {
        url = url.replace(types, 'past_hosted_events');
    }
    else if (type === enums_1.EventType.Upcoming) {
        url = url.replace(types, 'upcoming_hosted_events');
    }
    return `${url}?_fb_noscript=1`;
};
exports.validateAndFormatEventPageUrl = validateAndFormatEventPageUrl;
// Covers pages with the following format:
// https://www.facebook.com/profile.php?id=61553164865125&sk=events
// https://www.facebook.com/profile.php?id=61564982700539
// https://www.facebook.com/profile.php?id=61564982700539&sk=past_hosted_events
// https://www.facebook.com/profile.php?id=61564982700539&sk=upcoming_hosted_events
const validateAndFormatEventProfileUrl = (url, type) => {
    const regex = /facebook\.com\/profile\.php\?id=\d+(&sk=(events|past_hosted_events|upcoming_hosted_events))?$/;
    const result = regex.test(url);
    if (!result) {
        throw new Error('Invalid Facebook profile event URL');
    }
    const types = /(past_hosted_events|upcoming_hosted_events|events)$/;
    if (!types.test(url)) {
        if (type === enums_1.EventType.Past) {
            url += '&sk=past_hosted_events';
        }
        else if (type === enums_1.EventType.Upcoming) {
            url += '&sk=upcoming_hosted_events';
        }
        else {
            url += '&sk=events';
        }
    }
    else if (type === enums_1.EventType.Past) {
        url = url.replace(types, 'past_hosted_events');
    }
    else if (type === enums_1.EventType.Upcoming) {
        url = url.replace(types, 'upcoming_hosted_events');
    }
    return url;
};
exports.validateAndFormatEventProfileUrl = validateAndFormatEventProfileUrl;
// Covers pages with the following format:
// https://www.facebook.com/groups/409785992417637/events
// https://www.facebook.com/groups/409785992417637
// https://www.facebook.com/groups/zoukcr
const validateAndFormatEventGroupUrl = (url) => {
    const regex = /facebook\.com\/groups\/[a-zA-Z0-9]+(?:\/events$)?/;
    const result = regex.test(url);
    if (!result) {
        throw new Error('Invalid Facebook group event URL');
    }
    if (!url.match('/events')) {
        url += '/events';
    }
    return `${url}?_fb_noscript=1`;
};
exports.validateAndFormatEventGroupUrl = validateAndFormatEventGroupUrl;
