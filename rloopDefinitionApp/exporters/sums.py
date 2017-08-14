import json
import logging
import random

from rloopDefinitionApp.exporters.base import Exporter

log = logging.getLogger(__name__)

class Sums(Exporter):
    @property
    def sums(self) -> dict:
        """
            It's just a method to grab from the generator for now.
        """
        return self.generator.sums

    def export(self):
        if self.generator.md5_ok:
            # Did you really look at the code or did you not? ;)
            self.sums.update({
                "I_REALLY_LOOKED": random.randint(0, 65535),
            })

            with self.yield_file("file_sums.json") as f:
                json.dump(self.sums, f, indent=4)
        else:
            log.warning("Not saving updated checksums to disk.")
            log.warning(
                "Please review the recent changes for those files and rerun this script with environment "
                "variable I_REALLY_LOOKED=%s if you would like to save checksums to disk.",
                self.sums["I_REALLY_LOOKED"]
            )
