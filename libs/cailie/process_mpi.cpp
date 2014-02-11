
#include "cailie.h"
#include "utils.h"
#include <mpi.h>

using namespace ca;

/* This code is just proof of concept and it really needs some tweaks */

void Process::broadcast_packet(int tag, void *data, size_t size, Thread *thread, int exclude)
{
	thread->get_requests()->check();
	char *d = (char*) data;
	for (int t = 0; t < process_count; t++) {
		if (t == exclude)
			continue;
		MPI_Request *request = thread->get_requests()->new_request(d);
		d = NULL;
		MPI_Isend(data, size, MPI_BYTE, t, tag, MPI_COMM_WORLD, request);
	}
}

void Process::send_multicast(
	const std::vector<int> &targets,
	Net *net,
	int edge_id,
	int tokens_count,
	const Packer &packer,
	Thread *thread)
{
	thread->get_requests()->check();
	char *buffer = packer.get_buffer();
	size_t size = packer.get_size();
	std::vector<int>::const_iterator i;
	Tokens *data = (Tokens*) packer.get_buffer();
	data->edge_id = edge_id;
	data->tokens_count = tokens_count;
	char *d = buffer;
	for (i = targets.begin(); i != targets.end(); i++) {
		int target = *i;
		if(target < 0 || target >= process_count) {
			fprintf(stderr, "Net sends %i token(s) to invalid process id %i (valid ids: [0 .. %i])\n",
				tokens_count, target, process_count - 1);
			exit(1);
		}
		CA_DLOG("SEND index=%i target=%i process=%i\n", place_index, target, get_process_id());

		MPI_Request *request = thread->get_requests()->new_request(d);
		d = NULL;
		MPI_Isend(buffer, size, MPI_BYTE, target, CA_TAG_TOKENS, MPI_COMM_WORLD, request);
	}
}

int Process::process_packets(Thread *thread)
{
	int flag;
	MPI_Status status;
	MPI_Iprobe(MPI_ANY_SOURCE, MPI_ANY_TAG, MPI_COMM_WORLD, &flag, &status);

	if (flag) {
		bool net_changed = false;
		for(;;) {
			int msg_size;
			MPI_Get_count(&status, MPI_BYTE, &msg_size);
			char *buffer = (char*) malloc(msg_size); // FIXME: alloca for small packets
			MPI_Recv(buffer, msg_size, MPI_BYTE, MPI_ANY_SOURCE, MPI_ANY_TAG, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
			/* Now we have to be sure that all thread messages
			   are processed and we know about all nets */
			thread->process_thread_messages();
			net_changed |= process_packet(thread, status.MPI_SOURCE, status.MPI_TAG, buffer);

			MPI_Iprobe(MPI_ANY_SOURCE, MPI_ANY_TAG, MPI_COMM_WORLD, &flag, &status);
			if (!flag)
				break;
		}
		TraceLog *tracelog = thread->get_tracelog();
		if (net_changed && tracelog) {
			tracelog->event_end();
		}
		return 1;
	}
	return 0;
}

void Process::wait()
{
	MPI_Status status;
	MPI_Probe(MPI_ANY_SOURCE, MPI_ANY_TAG, MPI_COMM_WORLD, &status);

	int msg_size;
	MPI_Get_count(&status, MPI_BYTE, &msg_size);
	char *buffer = (char*) malloc(msg_size); // FIXME: alloca for small packets
	MPI_Recv(buffer, msg_size, MPI_BYTE, MPI_ANY_SOURCE, MPI_ANY_TAG, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
	this->get_thread(0)->process_thread_messages();
	process_packet(this->get_thread(0), status.MPI_SOURCE, status.MPI_TAG, buffer);
}

void ca::Process::collective_scatter_root(int transition_id, void *data, size_t size) {
	/**
	 * Root already knows scattered data, but MPI_Scatter want a pointer to memory, so we
	 * temporarily alloc some memory to satisfy the call
	 */
	void *out;
	if (size > 1024) {
		out = malloc(size);
		CA_ALLOC_TEST(out);
	} else {
		out = alloca(size);
	}
	MPI_Scatter(data, size, MPI_BYTE, out, size, MPI_BYTE, process_id, MPI_COMM_WORLD);
	if (size > 1024) {
		free(out);
	}
}

void ca::Process::collective_scatter_nonroot(int transition_id, int root, void *out, size_t size) {
	MPI_Scatter(NULL, size, MPI_BYTE, out, size, MPI_BYTE, root, MPI_COMM_WORLD);
}

