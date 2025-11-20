#!/bin/bash
# Common curl utilities
# Source this file to use common curl functions

# Get HTTP status code only
get_http_code() {
    local url=$1
    local timeout=${2:-10}
    local headers=${3:-""}

    local curl_cmd="curl -s -o /dev/null -w \"%{http_code}\" --max-time $timeout"

    if [ -n "$headers" ]; then
        curl_cmd="$curl_cmd -H \"$headers\""
    fi

    curl_cmd="$curl_cmd \"$url\" 2>/dev/null || echo \"000\""

    eval "$curl_cmd"
}

# Get full response with HTTP code
get_response_with_code() {
    local url=$1
    local timeout=${2:-10}
    local headers=${3:-""}

    local curl_cmd="curl -s -w \"\n%{http_code}\" --max-time $timeout"

    if [ -n "$headers" ]; then
        curl_cmd="$curl_cmd -H \"$headers\""
    fi

    curl_cmd="$curl_cmd \"$url\" 2>&1"

    eval "$curl_cmd"
}
