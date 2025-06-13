"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getCategories = exports.getEndTimestampAndTimezone = exports.getOnlineDetails = exports.getHosts = exports.getLocation = exports.getUserStats = exports.getTicketUrl = exports.getBasicData = exports.getDescription = void 0;
const json_1 = require("./json");
const getDescription = (html) => {
    const { jsonData } = (0, json_1.findJsonInString)(html, 'event_description');
    if (!jsonData) {
        throw new Error('No event description found, please verify that your event URL is correct');
    }
    return jsonData.text;
};
exports.getDescription = getDescription;
const getBasicData = (html) => {
    var _a, _b, _c, _d, _e, _f, _g, _h;
    const { jsonData } = (0, json_1.findJsonInString)(html, 'event', (candidate) => candidate.day_time_sentence);
    if (!jsonData) {
        throw new Error('No event data found, please verify that your URL is correct and the event is accessible without authentication');
    }
    return {
        id: jsonData.id,
        name: jsonData.name,
        photo: ((_a = jsonData.cover_media_renderer) === null || _a === void 0 ? void 0 : _a.cover_photo)
            ? {
                url: jsonData.cover_media_renderer.cover_photo.photo.url,
                id: jsonData.cover_media_renderer.cover_photo.photo.id,
                imageUri: (_c = (_b = jsonData.cover_media_renderer.cover_photo.photo.image) === null || _b === void 0 ? void 0 : _b.uri) !== null && _c !== void 0 ? _c : (_d = jsonData.cover_media_renderer.cover_photo.photo.full_image) === null || _d === void 0 ? void 0 : _d.uri
            }
            : null,
        video: ((_e = jsonData.cover_media_renderer) === null || _e === void 0 ? void 0 : _e.cover_video)
            ? {
                url: jsonData.cover_media_renderer.cover_video.url,
                id: jsonData.cover_media_renderer.cover_video.id,
                thumbnailUri: (_f = jsonData.cover_media_renderer.cover_video.image) === null || _f === void 0 ? void 0 : _f.uri
            }
            : null,
        formattedDate: jsonData.day_time_sentence,
        startTimestamp: jsonData.start_timestamp,
        isOnline: jsonData.is_online,
        url: jsonData.url,
        // Sibling events, for multi-date events
        siblingEvents: (_h = (_g = jsonData.comet_neighboring_siblings) === null || _g === void 0 ? void 0 : _g.map((sibling) => ({
            id: sibling.id,
            startTimestamp: sibling.start_timestamp,
            endTimestamp: sibling.end_timestamp,
            parentEvent: { id: sibling.parent_event.id }
        }))) !== null && _h !== void 0 ? _h : [],
        // If parent exists, and its not the same as the current event, set the parentEvent field
        parentEvent: jsonData.parent_if_exists_or_self &&
            jsonData.parent_if_exists_or_self.id !== jsonData.id
            ? { id: jsonData.parent_if_exists_or_self.id }
            : null
    };
};
exports.getBasicData = getBasicData;
const getTicketUrl = (html) => {
    var _a;
    const { jsonData } = (0, json_1.findJsonInString)(html, 'event', (candidate) => candidate.event_buy_ticket_url);
    // If the event doesnt have a ticket URL, jsonData will be null
    return (_a = jsonData === null || jsonData === void 0 ? void 0 : jsonData.event_buy_ticket_url) !== null && _a !== void 0 ? _a : null;
};
exports.getTicketUrl = getTicketUrl;
const getUserStats = (html) => {
    const { jsonData: usersRespondedJsonData } = (0, json_1.findJsonInString)(html, 'event_connected_users_public_responded');
    // usersRespondedJsonData can be undefined if the host decides to hide the guest list
    return {
        usersResponded: usersRespondedJsonData === null || usersRespondedJsonData === void 0 ? void 0 : usersRespondedJsonData.count
    };
};
exports.getUserStats = getUserStats;
// Only called for non-online events
const getLocation = (html) => {
    var _a, _b, _c, _d, _e, _f, _g, _h;
    const { jsonData, startIndex } = (0, json_1.findJsonInString)(html, 'event_place', (candidate) => 'location' in candidate);
    // If there is no start index, it means the event_place field wasn't found in the HTML
    if (startIndex === -1) {
        throw new Error('No location information found, please verify that your event URL is correct');
    }
    // If jsonData is null, it means we did find the event_place field but it was set to null. This happens for events with no locations set
    if (jsonData === null) {
        return null;
    }
    return {
        id: jsonData.id,
        name: jsonData.name,
        description: (_b = (_a = jsonData.best_description) === null || _a === void 0 ? void 0 : _a.text) !== null && _b !== void 0 ? _b : null,
        url: (_c = jsonData.url) !== null && _c !== void 0 ? _c : null,
        coordinates: jsonData.location
            ? {
                latitude: jsonData.location.latitude,
                longitude: jsonData.location.longitude
            }
            : null,
        countryCode: (_f = (_e = (_d = jsonData.location) === null || _d === void 0 ? void 0 : _d.reverse_geocode) === null || _e === void 0 ? void 0 : _e.country_alpha_two) !== null && _f !== void 0 ? _f : null,
        type: jsonData.place_type,
        address: (_h = (_g = jsonData.address) === null || _g === void 0 ? void 0 : _g.street) !== null && _h !== void 0 ? _h : null,
        city: jsonData.city
            ? {
                name: jsonData.city.contextual_name,
                id: jsonData.city.id
            }
            : null
    };
};
exports.getLocation = getLocation;
const getHosts = (html) => {
    const { jsonData } = (0, json_1.findJsonInString)(html, 'event_hosts_that_can_view_guestlist', 
    // We check for profile_picture field since there are other event_hosts_that_can_view_guestlist keys which have more limited host data (doesnt include profile_picture).
    (candidate) => { var _a; return (_a = candidate === null || candidate === void 0 ? void 0 : candidate[0]) === null || _a === void 0 ? void 0 : _a.profile_picture; });
    if (jsonData === null) {
        // This happens if the event is hosted by an external provider, eg https://www.facebook.com/events/252144510602906.
        // TODO: See if we can get any other data about the host (eg URL). Look at event_host_context_row_info field
        return [];
    }
    return jsonData.map((host) => ({
        id: host.id,
        name: host.name,
        url: host.url,
        type: host.__typename,
        photo: {
            imageUri: host.profile_picture.uri
        }
    }));
};
exports.getHosts = getHosts;
const getOnlineDetails = (html) => {
    const { jsonData } = (0, json_1.findJsonInString)(html, 'online_event_setup', (candidate) => 'third_party_url' in candidate && 'type' in candidate);
    if (jsonData === null) {
        throw new Error('No online event details found, please verify that your event URL is correct');
    }
    return { url: jsonData.third_party_url, type: jsonData.type };
};
exports.getOnlineDetails = getOnlineDetails;
const getEndTimestampAndTimezone = (html, expectedStartTimestamp) => {
    const { jsonData } = (0, json_1.findJsonInString)(html, 'data', (candidate) => 'end_timestamp' in candidate &&
        'tz_display_name' in candidate &&
        candidate.start_timestamp === expectedStartTimestamp);
    if (jsonData === null) {
        throw new Error('No end date & timezone details found, please verify that your event URL is correct');
    }
    // If event doesnt have an end date, end_timestamp will be set to 0
    return {
        endTimestamp: jsonData.end_timestamp || null,
        timezone: jsonData.tz_display_name
    };
};
exports.getEndTimestampAndTimezone = getEndTimestampAndTimezone;
const getCategories = (html) => {
    const { jsonData } = (0, json_1.findJsonInString)(html, 'discovery_categories');
    return jsonData;
};
exports.getCategories = getCategories;
