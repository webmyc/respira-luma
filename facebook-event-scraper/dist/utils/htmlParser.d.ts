import { EventData, EventLocation, EventHost, OnlineEventDetails, EventCategory } from '../types';
export declare const getDescription: (html: string) => string;
export declare const getBasicData: (html: string) => Pick<EventData, 'id' | 'name' | 'photo' | 'video' | 'formattedDate' | 'startTimestamp' | 'isOnline' | 'url' | 'siblingEvents' | 'parentEvent'>;
export declare const getTicketUrl: (html: string) => string;
export declare const getUserStats: (html: string) => {
    usersResponded: any;
};
export declare const getLocation: (html: string) => EventLocation | null;
export declare const getHosts: (html: string) => EventHost[];
export declare const getOnlineDetails: (html: string) => OnlineEventDetails;
export declare const getEndTimestampAndTimezone: (html: string, expectedStartTimestamp: number) => {
    endTimestamp: any;
    timezone: any;
};
export declare const getCategories: (html: string) => EventCategory[];
