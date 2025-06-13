import { EventType } from '../enums';
export declare const fbidToUrl: (fbid: string) => string;
export declare const validateAndFormatUrl: (url: string) => string;
export declare const validateAndFormatEventPageUrl: (url: string, type?: EventType) => string;
export declare const validateAndFormatEventProfileUrl: (url: string, type?: EventType) => string;
export declare const validateAndFormatEventGroupUrl: (url: string) => string;
