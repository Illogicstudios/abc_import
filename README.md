# ABC Import

ABC Import is a tool to import ABCs with versioning.

It pairs up with the ABC Export tool (https://github.com/Illogicstudios/abc_export)
and it requires the Look Loader tool (https://github.com/Illogicstudios/look_loader)

## How to install

You will need some files that several Illogic tools need. You can get them via this link :
https://github.com/Illogicstudios/common

---

## Features

### Retrieve Anims and Furs

<div align="center">
  <span>
    <img src="https://user-images.githubusercontent.com/94440879/219347243-0525e34d-dcf6-425d-8c7c-8554ac32bd87.png" width=30%>
  </span>
  <p weight="bold">Example of the file architecture built from the ABC Export tool that can be retrived with the ABC Import</p>
  <br/>
</div>

<div align="center">
  <span>
    <img src="https://github.com/Illogicstudios/look_loader/assets/117286626/022e7f04-1777-452b-9724-eff0d4db6161" width=60%>
  </span>
  <p weight="bold">You can retrieve the abc anim and the abc fur from a folder</p>
  <br/>
</div>

A valid folder is an existing folder named "abc" or "abc_fur" or the parent folder of one of these.

In the User interface you can visualize the available versions and if the assets are already in the scene. Here no assets are present.

<div align="center">
  <span>
    <img src="https://github.com/Illogicstudios/look_loader/assets/117286626/b3bd4b9e-ed05-4b76-b16e-7ff251750ca7" width=60%>
  </span>
  <p weight="bold">States change when assets are already in the scene</p>
  <br/>
</div>

### Importing and Updating

By selecting a row and clicking the button "Import or Update selection" the abc will be update or import to the version selected in the "Import version" of the abc.

The "look" icons show if the looks and uvs are out of dates.

The checkbox "Set last Looks" updates the looks to the last looks and uvs.
