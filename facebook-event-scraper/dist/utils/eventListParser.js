"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getEventListFromGroup = exports.getEventListFromPageOrProfile = void 0;
const json_1 = require("./json");
const enums_1 = require("../enums");
const getEventListFromPageOrProfile = (html) => {
    const { jsonData } = (0, json_1.findJsonInString)(html, 'collection');
    if (!jsonData) {
        throw new Error('No event data found, please verify that your URL is correct and the events are accessible without authentication');
    }
    const events = [];
    jsonData.pageItems.edges.forEach((event) => {
        events.push({
            id: event.node.node.id,
            name: event.node.node.name,
            url: event.node.node.url,
            date: event.node.node.day_time_sentence,
            isCanceled: event.node.node.is_canceled,
            isPast: event.node.actions_renderer.event.is_past
        });
    });
    return events;
};
exports.getEventListFromPageOrProfile = getEventListFromPageOrProfile;
const getEventListFromGroup = (html, type = enums_1.EventType.Upcoming) => {
    const { jsonData } = (0, json_1.findJsonInString)(html, type === enums_1.EventType.Upcoming ? 'upcoming_events' : 'past_events');
    if (!jsonData) {
        throw new Error('No event data found, please verify that your URL is correct and the events are accessible without authentication');
    }
    const events = [];
    if (jsonData.edges.length > 0) {
        jsonData.edges.forEach((event) => {
            events.push({
                id: event.node.id,
                name: event.node.name,
                url: event.node.url,
                date: event.node.day_time_sentence,
                isCanceled: event.node.is_canceled,
                isPast: event.node.is_past
            });
        });
    }
    return events;
};
exports.getEventListFromGroup = getEventListFromGroup;
