# Changelog

All notable changes to Unthinking Majority's website will be documented in this file.

The format of this document is loosely based on [Keep a Changelog](https://keepachangelog.com/).

# 2023-11-2

### Added

* New PVM_SPLIT_POINTS_MAX setting under the `config` admin, which limits the amounts of dragonstone points earnable
  from pvm splits
* New method of obtaining dragonstone points: New Member Raid
    * Raid with a new member (rank Sapphire or Emerald) to obtain points
    * Default is 2 points obtained for a raid with a new member

### Changed

# 2023-11-1

### Changed

* Dragonstone system overhaul
    * Introduction of DragonstonePoints models
* Settings model has been removed, and replaced with the `django-constance` package
    * Settings/configuration variables can now be found under Settings->Config in the admin

# 2023-10-29

### Added

* Dragonstone points threshold is now configurable via the DRAGONSTONE_POINTS_THRESHOLD object in the Settings admin

# 2023-10-27

### Added

* Expiration period for Dragonstone submissions is now configurable via the DRAGONSTONE_EXPIRATION_PERIOD object in the
  Settings admin
* Preferred name features for users
    * Preferred names will now be displayed in place of the user in game name if available
    * User can change their preferred name by going to their profile page and following the link from there

### Changed

* Authenticated users no longer need to fill out user field for solo submissions
* Achievements and Dragonstone models now utilize django polymorhpic
    * Admin interfaces for both should look much cleaner now!

