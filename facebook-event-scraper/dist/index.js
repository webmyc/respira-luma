"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.scrapeFbEventList = exports.scrapeFbEventListFromGroup = exports.scrapeFbEventListFromProfile = exports.scrapeFbEventListFromPage = exports.scrapeFbEventFromFbid = exports.scrapeFbEvent = exports.EventType = void 0;
const url_1 = require("./utils/url");
const eventListParser = __importStar(require("./utils/eventListParser"));
const scraper_1 = require("./scraper");
const network_1 = require("./utils/network");
const enums_1 = require("./enums");
Object.defineProperty(exports, "EventType", { enumerable: true, get: function () { return enums_1.EventType; } });
const scrapeFbEvent = (url, options = {}) => __awaiter(void 0, void 0, void 0, function* () {
    const formattedUrl = (0, url_1.validateAndFormatUrl)(url);
    return yield (0, scraper_1.scrapeEvent)(formattedUrl, options);
});
exports.scrapeFbEvent = scrapeFbEvent;
const scrapeFbEventFromFbid = (fbid, options = {}) => __awaiter(void 0, void 0, void 0, function* () {
    const formattedUrl = (0, url_1.fbidToUrl)(fbid);
    return yield (0, scraper_1.scrapeEvent)(formattedUrl, options);
});
exports.scrapeFbEventFromFbid = scrapeFbEventFromFbid;
const scrapeFbEventListFromPage = (url, type, options = {}) => __awaiter(void 0, void 0, void 0, function* () {
    const formattedUrl = (0, url_1.validateAndFormatEventPageUrl)(url, type);
    const dataString = yield (0, network_1.fetchEvent)(formattedUrl, options.proxy);
    return eventListParser.getEventListFromPageOrProfile(dataString);
});
exports.scrapeFbEventListFromPage = scrapeFbEventListFromPage;
const scrapeFbEventListFromProfile = (url, type, options = {}) => __awaiter(void 0, void 0, void 0, function* () {
    const formattedUrl = (0, url_1.validateAndFormatEventProfileUrl)(url, type);
    const dataString = yield (0, network_1.fetchEvent)(formattedUrl, options.proxy);
    return eventListParser.getEventListFromPageOrProfile(dataString);
});
exports.scrapeFbEventListFromProfile = scrapeFbEventListFromProfile;
const scrapeFbEventListFromGroup = (url, type, options = {}) => __awaiter(void 0, void 0, void 0, function* () {
    const formattedUrl = (0, url_1.validateAndFormatEventGroupUrl)(url);
    const dataString = yield (0, network_1.fetchEvent)(formattedUrl, options.proxy);
    return eventListParser.getEventListFromGroup(dataString, type);
});
exports.scrapeFbEventListFromGroup = scrapeFbEventListFromGroup;
const scrapeFbEventList = (url, type, options = {}) => __awaiter(void 0, void 0, void 0, function* () {
    if (url.includes('/groups/')) {
        return (0, exports.scrapeFbEventListFromGroup)(url, type, options);
    }
    if (url.includes('/profile.php')) {
        return (0, exports.scrapeFbEventListFromProfile)(url, type, options);
    }
    return (0, exports.scrapeFbEventListFromPage)(url, type, options);
});
exports.scrapeFbEventList = scrapeFbEventList;
