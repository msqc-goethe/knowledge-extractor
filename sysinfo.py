import platform
import re
import traceback
import subprocess
import json


class Sysmodel:
  def __init__(self, name=-1, kernel_version=-1, processor_architecture=-1, processor_model=-1,
               processor_frequency=-1, processor_threads=-1, processor_vendor=-1, processor_L2=-1,
               processor_L3=-1, processor_coresPerSocket=-1, distribution=-1, distribution_version=-1, memory_capacity=-1):
    self.name = name
    self.kernel_version =kernel_version
    self.processor_architecture=processor_architecture
    self.processor_model=processor_model
    self.processor_frequency=processor_frequency
    self.processor_threads=processor_threads
    self.processor_vendor=processor_vendor
    self.processor_L2=processor_L2
    self.processor_L3=processor_L3
    self.processor_coresPerSocket=processor_coresPerSocket
    self.distribution=distribution
    self.distribution_version=distribution_version
    self.memory_capacity=memory_capacity

  def SysmodelToJSON(self):
    sys = [{
      "name": self.name,
      "kernel_version": self.kernel_version,
      "processor_architecture": self.processor_architecture,
      "processor_model": self.processor_model,
      "processor_frequency": self.processor_frequency,
      "processor_threads": self.processor_threads,
      "processor_vendor": self.processor_vendor,
      "processor_L2": self.processor_L2,
      "processor_L3": self.processor_L3,
      "processor_coresPerSocket": self.processor_coresPerSocket,
      "distribution": self.distribution,
      "distribution_version": self.distribution_version,
      "memory_capacity": self.memory_capacity
    }]

    return sys

def re_add(regex, key, data, group=1):
  m = re.search(regex, data)
  if m:
    print(key, m.group(group))


def get_sys_info():
  sysinfo = Sysmodel()
  return sysinfo
  sysinfo.name = platform.node()
  sysinfo.kernel_version = platform.release()
  sysinfo.processor_architecture = platform.processor()

  # CPU Information
  data = open("/proc/cpuinfo", "r").read()
  model_set = False
  cores = 0
  for line in data.split("\n"):
    if "model name" in line and not model_set:
      m = re.match("model name.*: ([^@]*)(@ ([0-9.]*)GHz)?", line)
      if m:
        cpu = m.group(1).strip()
        if cpu.find("CPU") > -1:
          cpu = cpu.replace("CPU", "")
        cpu = re.sub("\([^)]*\)", "", cpu)
        sysinfo.processor_model= cpu
        #should check cpu MHz, but also other / more metrics are available.
        if m.group(3):
          print("Processor.frequency", m.group(3), "GHz")
          tmp = str(m.group(3)) + "GHz"
          sysinfo.processor_frequency = tmp
        model_set = True
    if line.startswith("processor"):
      cores = cores + 1

  try:
    data = subprocess.check_output("LANG=C lscpu", shell=True, universal_newlines=True).strip()
    m = re.search("Core\(s\) per socket: *([0-9]+)", data)
    if m:
      cores = m.group(1)

    m = re.search("Thread\(s\) per core: *([0-9]+)", data)
    if m:
      sysinfo.processor_threads = m.group(1)

    m = re.search("Vendor ID: *(.*)", data)
    if m:
      sysinfo.processor_vendor = m.group(1)

    m = re.search("L2 cache: *([0-9]+.*)", data)
    if m:
      sysinfo.processor_L2 = m.group(1)

    m = re.search("L3 cache: *([0-9]+.*)", data)
    if m:
      sysinfo.processor_L3 = m.group(1)

  except:
    traceback.print_exc()
    print("Cannot execute lscpu, will continue")
  sysinfo.processor_coresPerSocket = cores

  # OS Information
  kv = {}
  with open("/etc/os-release") as f:
    for line in f:
      arr = line.split("=")
      if len(arr) == 2:
        kv[arr[0].strip()] = arr[1].strip(" \n\t\"")

  if "ID" in kv:
    val = kv["ID"]
    if val == "ubuntu":
      val = "Ubuntu"
    sysinfo.distribution = val
  if "VERSION_ID" in kv:
    sysinfo.distribution_version = kv["VERSION_ID"]

  # Try to add memory
  with open("/proc/meminfo") as f:
    for line in f:
      arr = line.split(":")
      if len(arr) == 2:
        kv[arr[0].strip()] = arr[1].strip(" \n\t\"")
    if "MemTotal" in kv:
     sysinfo.memory_capacity = kv["MemTotal"].replace("kB", "KiB")

  return sysinfo


