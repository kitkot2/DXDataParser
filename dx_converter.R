#!/usr/bin/env Rscript
args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 1) {
  stop("Please specify a DX file for conversion", call. = FALSE)
}

dx_file <- args[1]
mode <- ifelse(length(args) >= 2, args[2], "clean")

# Check and install required packages if needed
required_packages <- c("chromConverter", "xml2", "data.table")
missing_packages <- setdiff(required_packages, rownames(installed.packages()))

if (length(missing_packages) > 0) {
  message("Installing required packages: ", paste(missing_packages, collapse = ", "))
  install.packages(missing_packages, repos = "https://cloud.r-project.org")
}

library(chromConverter)
library(xml2)
library(data.table)

# Conversion function
convert_dx_to_csv <- function(dx_file, mode = "clean") {
  original_wd <- getwd()
  on.exit(setwd(original_wd))
  
  script_dir <- NULL
  if (!interactive()) {
    script_dir <- dirname(sub("--file=", "", commandArgs()[grep("--file=", commandArgs())]))
  } else if (requireNamespace("rstudioapi", quietly = TRUE)) {
    script_dir <- dirname(rstudioapi::getActiveDocumentContext()$path)
  }
  
  if (!is.null(script_dir)) {
    setwd(script_dir)
    message("Working directory set to: ", getwd())
  } else {
    warning("Unable to determine script directory, using current: ", getwd())
  }
  
  if (!file.exists(dx_file)) {
    stop("File '", dx_file, "' not found in directory: ", getwd())
  }
  
  mode <- tolower(as.character(mode))
  
  output_dir <- sub("\\.dx$", "", dx_file, ignore.case = TRUE)
  if (!dir.exists(output_dir)) {
    dir.create(output_dir)
  }
  
  temp_dir <- tempfile(pattern = "dx_unpack_")
  dir.create(temp_dir)
  
  unzip(dx_file, exdir = temp_dir)
  
  all_files <- list.files(temp_dir, full.names = TRUE, recursive = TRUE)
  
  files_ch_uv <- grep("\\.(CH|UV)$", all_files, ignore.case = TRUE, value = TRUE)
  for (file in files_ch_uv) {
    ext <- toupper(tools::file_ext(file))
    csv_name <- sub(paste0("\\.", ext, "$"), ".csv", basename(file))
    csv_path <- file.path(output_dir, csv_name)
    
    if (ext == "CH") {
      dt <- read_chemstation_ch(file,
                              format_out = "data.table",
                              data_format = "wide",
                              read_metadata = FALSE)
      fwrite(dt, csv_path)
    } else if (ext == "UV") {
      dt <- read_chemstation_uv(file,
                              format_out = "data.table",
                              data_format = "wide",
                              read_metadata = FALSE)
      fwrite(dt, csv_path)
    }
  }
  
  if (mode == "clean" || mode == "1") {
    pattern <- "\\.(acmd|xml)$"
  } else {
    pattern <- ".*"
  }
  
  files_to_copy <- setdiff(all_files, files_ch_uv)
  files_to_copy <- grep(pattern, files_to_copy, ignore.case = TRUE, value = TRUE)
  
  for (file in files_to_copy) {
    file.copy(file, file.path(output_dir, basename(file)), overwrite = TRUE)
  }
  
  unlink(temp_dir, recursive = TRUE)
  
  message("Processed file: ", dx_file, " → results in ", output_dir, " (mode: ", mode, ")")
}

# Execute conversion with command line arguments
tryCatch({
  convert_dx_to_csv(dx_file, mode)
}, error = function(e) {
  message("Error: ", e$message)
  quit(status = 1)
})