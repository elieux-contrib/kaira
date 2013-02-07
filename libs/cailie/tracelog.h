
#ifndef CAILIE_TRACER_H
#define CAILIE_TRACER_H

#include <string>
#include <time.h>
#include <string.h>
#include <stdint.h>
#include <stdio.h>

namespace ca {

class TraceLog {

	public:

		TraceLog(size_t size, const std::string &filename);
		~TraceLog();

		void event_net_spawn(int net_id);
		void event_net_quit();
		void event_transition_fired(int transition_id);
		void event_transition_finished();
		void event_send_msg(int msg_id);
		void event_receive(int msg_id);
		void event_idle();

		void trace_token_add(int place_id, void *pointer);
		void trace_token_remove(int place_id, void *pointer);

		void trace_value(const int value);
		void trace_value(const double value);
		void trace_value(const std::string &str);

		static void init();
		static void write_head(const std::string &name);
	protected:

		void check_size(size_t size) { if (pos + size >= end) { overflow(); } }
		void write_char(char c) { *(pos++) = c; }

		void write_uint64(uint64_t value) {
			memcpy(pos, &value, sizeof(uint64_t));
			pos += sizeof(uint64_t);
		}

		void write_int32(int32_t value) {
			memcpy(pos, &value, sizeof(int32_t));
			pos += sizeof(int32_t);
		}

		void write_pointer(void *p) {
			memcpy(pos, &p, sizeof(void*));
			pos += sizeof(void*);
		}

		void write_string(const std::string &str) {
			size_t s = str.size();
			memcpy(pos, str.data(), s);
			pos += s;
			*(pos) = 0;
			pos++;
		}

		void write_double(const double value) {
			memcpy(pos, &value, sizeof(double));
			pos += sizeof(double);
		}

		void write_key_value(const std::string &key, const std::string &value);

		void write_buffer();

		void write_time();
		void overflow();

		char * buffer;
		char * pos;
		char * end;

		FILE * file;

		static struct timespec initial_time;

};

}

#endif // CAILIE_TRACER_H
