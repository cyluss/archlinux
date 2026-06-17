#define _DEFAULT_SOURCE
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/statvfs.h>
#include <sys/sysinfo.h>

int main() {
    printf("{\"version\":1}\n[\n[]\n");
    fflush(stdout);
    while (1) {
        char ip[96] = "no network";
        FILE *f = popen("ip -4 -o addr show scope global 2>/dev/null", "r");
        if (f) {
            char buf[256], iface[32], addr[64];
            if (fgets(buf, sizeof(buf), f))
                if (sscanf(buf, "%*d: %31s inet %63[^/]", iface, addr) == 2)
                    snprintf(ip, sizeof(ip), "%s: %s", iface, addr);
            pclose(f);
        }

        struct statvfs sv;
        statvfs("/", &sv);
        double disk = (double)sv.f_bavail * sv.f_frsize / (1024*1024*1024);

        double load0 = 0;
        FILE *lf = fopen("/proc/loadavg", "r");
        if (lf) { fscanf(lf, "%lf", &load0); fclose(lf); }

        struct sysinfo si;
        sysinfo(&si);
        long used = (si.totalram - si.freeram - si.bufferram - si.sharedram) / 1024 / 1024;
        long total = si.totalram / 1024 / 1024;

        char timebuf[32];
        time_t t = time(NULL);
        strftime(timebuf, sizeof(timebuf), "%Y-%m-%d %H:%M:%S", localtime(&t));

        printf(",["
            "{\"full_text\":\"%s\",\"color\":\"#0055aa\"},"
            "{\"full_text\":\"disk: %.1fG\"},"
            "{\"full_text\":\"load: %.2f\"},"
            "{\"full_text\":\"mem: %ld/%ldM\"},"
            "{\"full_text\":\"%s\"},"
            "{\"full_text\":\" \"}"
            "]\n", ip, disk, load0, used, total, timebuf);
        fflush(stdout);
        sleep(5);
    }
}
