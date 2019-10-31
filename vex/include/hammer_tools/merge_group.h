#pragma once
#ifndef _MERGE_GROUP_H_
#define _MERGE_GROUP_H_

int
merge_group(const int old_value;
            const int new_value;
            const int mode)
{
    if (mode == 0)  // Replace
        return new_value;
    else if (mode == 1)  // Union
        return max(old_value, new_value);
    else if (mode == 2)  // Intersect
        return old_value * new_value;
    else if (mode == 3) // Subtract
        return max(old_value - new_value, 0);
    error('Invalid merge mode');
    return -1;
}

#endif  // _MERGE_GROUP_H_
