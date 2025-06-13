import { EventData, ScrapeOptions, ShortEventData } from './types';
import { EventType } from './enums';
export { EventData, ScrapeOptions, ShortEventData, EventType };
export declare const scrapeFbEvent: (url: string, options?: ScrapeOptions) => Promise<EventData>;
export declare const scrapeFbEventFromFbid: (fbid: string, options?: ScrapeOptions) => Promise<EventData>;
export declare const scrapeFbEventListFromPage: (url: string, type?: EventType, options?: ScrapeOptions) => Promise<ShortEventData[]>;
export declare const scrapeFbEventListFromProfile: (url: string, type?: EventType, options?: ScrapeOptions) => Promise<ShortEventData[]>;
export declare const scrapeFbEventListFromGroup: (url: string, type?: EventType, options?: ScrapeOptions) => Promise<ShortEventData[]>;
export declare const scrapeFbEventList: (url: string, type?: EventType, options?: ScrapeOptions) => Promise<ShortEventData[]>;
