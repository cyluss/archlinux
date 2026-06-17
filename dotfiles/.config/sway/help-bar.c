#include <stdio.h>
#include <unistd.h>

int main() {
    printf("{\"version\":1}\n[\n[]\n");
    fflush(stdout);
    while (1) {
        printf(",["
            "{\"full_text\":\"term:Mod+Enter  run:Ctrl+Space  "
            "split:Mod+h  full:Mod+f  kill:Mod+Shift+q  "
            "reload:Mod+Shift+r  exit:Mod+Shift+e  "
            "IME:Mod+Space\","
            "\"color\":\"#888888\"}"
            "]\n");
        fflush(stdout);
        sleep(60);
    }
}
