// Auto-generated. Do not edit!

// (in-package pal_interaction_msgs.msg)


"use strict";

const _serializer = _ros_msg_utils.Serialize;
const _arraySerializer = _serializer.Array;
const _deserializer = _ros_msg_utils.Deserialize;
const _arrayDeserializer = _deserializer.Array;
const _finder = _ros_msg_utils.Find;
const _getByteLength = _ros_msg_utils.getByteLength;
let TtsMark = require('./TtsMark.js');

//-----------------------------------------------------------

class TtsFeedback {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.event_type = null;
      this.timestamp = null;
      this.text_said = null;
      this.next_word = null;
      this.viseme_id = null;
      this.marks = null;
    }
    else {
      if (initObj.hasOwnProperty('event_type')) {
        this.event_type = initObj.event_type
      }
      else {
        this.event_type = 0;
      }
      if (initObj.hasOwnProperty('timestamp')) {
        this.timestamp = initObj.timestamp
      }
      else {
        this.timestamp = {secs: 0, nsecs: 0};
      }
      if (initObj.hasOwnProperty('text_said')) {
        this.text_said = initObj.text_said
      }
      else {
        this.text_said = '';
      }
      if (initObj.hasOwnProperty('next_word')) {
        this.next_word = initObj.next_word
      }
      else {
        this.next_word = '';
      }
      if (initObj.hasOwnProperty('viseme_id')) {
        this.viseme_id = initObj.viseme_id
      }
      else {
        this.viseme_id = '';
      }
      if (initObj.hasOwnProperty('marks')) {
        this.marks = initObj.marks
      }
      else {
        this.marks = new TtsMark();
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type TtsFeedback
    // Serialize message field [event_type]
    bufferOffset = _serializer.uint16(obj.event_type, buffer, bufferOffset);
    // Serialize message field [timestamp]
    bufferOffset = _serializer.time(obj.timestamp, buffer, bufferOffset);
    // Serialize message field [text_said]
    bufferOffset = _serializer.string(obj.text_said, buffer, bufferOffset);
    // Serialize message field [next_word]
    bufferOffset = _serializer.string(obj.next_word, buffer, bufferOffset);
    // Serialize message field [viseme_id]
    bufferOffset = _serializer.string(obj.viseme_id, buffer, bufferOffset);
    // Serialize message field [marks]
    bufferOffset = TtsMark.serialize(obj.marks, buffer, bufferOffset);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type TtsFeedback
    let len;
    let data = new TtsFeedback(null);
    // Deserialize message field [event_type]
    data.event_type = _deserializer.uint16(buffer, bufferOffset);
    // Deserialize message field [timestamp]
    data.timestamp = _deserializer.time(buffer, bufferOffset);
    // Deserialize message field [text_said]
    data.text_said = _deserializer.string(buffer, bufferOffset);
    // Deserialize message field [next_word]
    data.next_word = _deserializer.string(buffer, bufferOffset);
    // Deserialize message field [viseme_id]
    data.viseme_id = _deserializer.string(buffer, bufferOffset);
    // Deserialize message field [marks]
    data.marks = TtsMark.deserialize(buffer, bufferOffset);
    return data;
  }

  static getMessageSize(object) {
    let length = 0;
    length += object.text_said.length;
    length += object.next_word.length;
    length += object.viseme_id.length;
    length += TtsMark.getMessageSize(object.marks);
    return length + 22;
  }

  static datatype() {
    // Returns string type for a message object
    return 'pal_interaction_msgs/TtsFeedback';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return '05870cd8b62fcb00e76ae3889c0ed8f1';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    # ====== DO NOT MODIFY! AUTOGENERATED FROM AN ACTION DEFINITION ======
    ## feedback
    
    # Everytime one of the following events occuring
    # during the synthesis process a feedback message
    # will be published.
    # Only TTS_EVENT_STARTED_PLAYING_WORD and 
    # TTS_EVENT_MARK are implemented now.
    
    uint16 TTS_EVENT_INITIALIZATION = 1
    uint16 TTS_EVENT_SHUTDOWN = 2
    uint16 TTS_EVENT_SYNCHRONIZATION = 4
    uint16 TTS_EVENT_FINISHED_PLAYING_UTTERANCE = 8
    uint16 TTS_EVENT_MARK = 16
    uint16 TTS_EVENT_STARTED_PLAYING_WORD = 32
    uint16 TTS_EVENT_FINISHED_PLAYING_PHRASE = 64
    uint16 TTS_EVENT_FINISHED_PLAYING_SENTENCE = 128
    uint16 TTS_EVENT_VISEME = 256
    
    # Store the event type and can be used
    # to filter messages depending on the type of 
    # events we are interested in
    
    uint16 event_type
    
    # Time since the begining of the synthesis
    # at which the event occured.
    
    time timestamp
    
    # Text said until now, 
    # it will contain the current word in case of WORD events
    
    string text_said
    
    # Next word to be pronounced
    # (not implemented)
    string next_word
    
    string viseme_id
    
    # Everytime a mark like this one
    # <mark name="markname"/> is present in the text
    # a MARK event will be generated with the 'name' 
    # argument value as mark id. Other fields
    # different from the mark_id are not implemented.
    
    TtsMark marks
    
    
    ================================================================================
    MSG: pal_interaction_msgs/TtsMark
    # id will contain the value of name argument in the <mark/>
    # tags when they are placed in synthesised text.
    # Filling keys and value is not implemented yet.
    string id
    string[] keys
    string[] value
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new TtsFeedback(null);
    if (msg.event_type !== undefined) {
      resolved.event_type = msg.event_type;
    }
    else {
      resolved.event_type = 0
    }

    if (msg.timestamp !== undefined) {
      resolved.timestamp = msg.timestamp;
    }
    else {
      resolved.timestamp = {secs: 0, nsecs: 0}
    }

    if (msg.text_said !== undefined) {
      resolved.text_said = msg.text_said;
    }
    else {
      resolved.text_said = ''
    }

    if (msg.next_word !== undefined) {
      resolved.next_word = msg.next_word;
    }
    else {
      resolved.next_word = ''
    }

    if (msg.viseme_id !== undefined) {
      resolved.viseme_id = msg.viseme_id;
    }
    else {
      resolved.viseme_id = ''
    }

    if (msg.marks !== undefined) {
      resolved.marks = TtsMark.Resolve(msg.marks)
    }
    else {
      resolved.marks = new TtsMark()
    }

    return resolved;
    }
};

// Constants for message
TtsFeedback.Constants = {
  TTS_EVENT_INITIALIZATION: 1,
  TTS_EVENT_SHUTDOWN: 2,
  TTS_EVENT_SYNCHRONIZATION: 4,
  TTS_EVENT_FINISHED_PLAYING_UTTERANCE: 8,
  TTS_EVENT_MARK: 16,
  TTS_EVENT_STARTED_PLAYING_WORD: 32,
  TTS_EVENT_FINISHED_PLAYING_PHRASE: 64,
  TTS_EVENT_FINISHED_PLAYING_SENTENCE: 128,
  TTS_EVENT_VISEME: 256,
}

module.exports = TtsFeedback;
